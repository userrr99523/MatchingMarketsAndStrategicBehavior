
from mapel.marriages.cultures.impartial import generate_asymmetric_votes
import mapel.core.features.mallows as ml


def generate_mallows_votes(*args, **kwargs):
    return ml.generate_mallows_votes(*args, **kwargs)


def generate_norm_mallows_votes(num_agents=None,
                                normphi=0.5,
                                weight=0.,
                                **kwargs):

    phi = ml.phi_from_normphi(num_agents, normphi=normphi)

    return generate_mallows_votes(num_agents, num_agents, phi)


def generate_mallows_asymmetric_votes(num_agents: int = None,
                                      phi_m: float = None,
                                      phi_w: float = None,
                                      **kwargs):
    """ Mallows on top of Asymmetric instance """

    votes_left, votes_right = generate_asymmetric_votes(num_agents=num_agents)

    votes_left = mallows_votes(votes_left, phi_m)
    votes_right = mallows_votes(votes_right, phi_w)

    for i in range(len(votes_left)):
        for j in range(len(votes_left[i])):
            votes_left[i][j] = votes_left[i][j] + 1
    for i in range(len(votes_right)):
        for j in range(len(votes_right[i])):
            votes_right[i][j] = votes_right[i][j] + 1

    return [votes_left, votes_right]


def mallows_vote(vote, phi):
    num_candidates = len(vote)
    raw_vote = generate_mallows_votes(1, num_candidates, phi=phi, weight=0)[0]
    new_vote = [0] * len(vote)
    for i in range(num_candidates):
        new_vote[raw_vote[i]] = vote[i]
    return new_vote


def mallows_votes(votes, phi):
    for i in range(len(votes)):
        votes[i] = mallows_vote(votes[i], phi)
    return votes

def generate_symmetric_votes_from_asymmetric(num_agents: int = None, **kwargs):
    # initialize votes with -1
    votes_left = [[-1]*num_agents for _ in range(num_agents)]
    votes_right = [[-1]*num_agents for _ in range(num_agents)]
 
    # each agent ranks themselves first
    for i in range(num_agents):
        votes_left[i][0] = i
        votes_right[i][0] = i
 
    # now fill mutual preferences
    pos = 1
    for i in range(num_agents):
        for j in range(i+1, num_agents):
            # assign i and j to each other at the same position
            votes_left[i][pos] = j
            votes_left[j][pos] = i
            votes_right[i][pos] = j
            votes_right[j][pos] = i
            pos += 1
            if pos == num_agents:
                pos = 1
 
    return [votes_left, votes_right]


def generate_mallows_MA_votes(num_agents: int = None,
                                      phi_m: float = None,
                                      phi_w: float = None,
                                      **kwargs):
    """ Mallows on top of Asymmetric instance """

    votes_left, votes_right = generate_symmetric_votes_from_asymmetric(num_agents=num_agents)

    votes_left = mallows_votes(votes_left, phi_m)
    votes_right = mallows_votes(votes_right, phi_w)

    for i in range(len(votes_left)):
        for j in range(len(votes_left[i])):
            votes_left[i][j] = votes_left[i][j] + 1
    for i in range(len(votes_right)):
        for j in range(len(votes_right[i])):
            votes_right[i][j] = votes_right[i][j] + 1

    return [votes_left, votes_right]
