"""Voting and election management system.

Registers voters, casts votes before the polls close, imports postal
ballots, tallies the results and reports the winner, vote share and turnout.
"""
import hashlib
import secrets
from datetime import datetime
from xml.parsers.expat import ExpatError

from defusedxml import pulldom, DefusedXmlException

VOTING_AGE = 18
POLLS_CLOSE_HOUR = 18
START_ELEMENT = "START_ELEMENT"  # same value as xml.dom.pulldom.START_ELEMENT
voters = {}
ballots = []
candidates = ["Alice", "Bob", "NOTA"]

def register_voter(voter_id, name, age):
    """Register a voter who is at least VOTING_AGE. Returns True on success."""
    if age < VOTING_AGE or voter_id in voters:
        return False
    id_hash = hashlib.sha256(voter_id.encode()).hexdigest()
    voters[voter_id] = {"name": name, "hash": id_hash, "voted": False, "receipt": None}
    return True

def is_officer(role):
    """Return True only for the election officer role."""
    return role == "officer"

def normalise_candidate(candidate):
    """Return the official spelling of a candidate name, or None if unknown."""
    for official in candidates:
        if official.lower() == candidate.strip().lower():
            return official
    return None

def record_ballot(voter_id, candidate):
    """Record one ballot for an eligible voter. Returns a receipt or None."""
    voter = voters.get(voter_id)
    official = normalise_candidate(candidate)
    if voter is None or voter["voted"] or official is None:
        return None
    ballots.append(official)
    voter["voted"] = True
    voter["receipt"] = receipt_number()
    return voter["receipt"]

def cast_vote(voter_id, candidate, when):
    """Cast an in-person vote. Polls close at POLLS_CLOSE_HOUR:00 sharp."""
    if when.hour >= POLLS_CLOSE_HOUR:
        return False
    return record_ballot(voter_id, candidate) is not None

def tally():
    """Return a dict of candidate -> number of ballots."""
    counts = {name: 0 for name in candidates}
    for ballot in ballots:
        counts[ballot] += 1
    return counts

def winner():
    """Return the candidate with the most votes, or None if no votes or a tie."""
    counts = tally()
    top = max(counts.values())
    leaders = [name for name, count in counts.items() if count == top]
    if top == 0 or len(leaders) > 1:
        return None
    return leaders[0]

def vote_percent(name):
    """Return the share of ballots for a candidate, rounded to 2 places."""
    if not ballots:
        return 0.0
    return round(tally().get(name, 0) * 100 / len(ballots), 2)

def turnout():
    """Return the percentage of registered voters who have voted."""
    if not voters:
        return 0.0
    voted = sum(1 for voter in voters.values() if voter["voted"])
    return round(voted * 100 / len(voters), 2)

def count_for(candidate, ballot_list):
    """Count how many ballots in ballot_list are for candidate."""
    return sum(1 for ballot in ballot_list if ballot == candidate)

def announce():
    """Return one result line per candidate."""
    counts = tally()
    return [f"{name}: {counts[name]}" for name in candidates]

def receipt_number():
    """Return an unpredictable receipt number."""
    return "RCPT-" + str(secrets.randbelow(900000) + 100000)

def import_postal_ballots(xml_text):
    """Import postal ballots from XML, accepting only eligible voters."""
    events = pulldom.parseString(xml_text)
    imported = 0
    try:
        for event, node in events:
            if event == START_ELEMENT and node.tagName == "ballot":
                voter_id = node.getAttribute("voter")
                if record_ballot(voter_id, node.getAttribute("candidate")) is not None:
                    imported += 1
    except (DefusedXmlException, ExpatError) as err:
        raise ValueError("Rejected unsafe or malformed postal ballot XML") from err
    return imported

def main():
    """Run a sample election."""
    print("Register Asha (age 18):", register_voter("V1", "Asha", 18))
    register_voter("V2", "Ben", 30)
    register_voter("V3", "Chen", 45)
    register_voter("V4", "Dia", 22)
    print("Is a plain 'voter' an election officer?", is_officer("voter"))
    print("Ben votes Alice:", cast_vote("V2", "Alice", datetime(2026, 11, 20, 10, 0)))
    print("Ben votes Alice again:", cast_vote("V2", "Alice", datetime(2026, 11, 20, 11, 0)))
    print("Chen votes 'bob':", cast_vote("V3", "bob", datetime(2026, 11, 20, 12, 0)))
    print("Dia votes Bob at 18:30:", cast_vote("V4", "Bob", datetime(2026, 11, 20, 18, 30)))
    postal_xml = "<postal><ballot voter='V1' candidate='Bob'/></postal>"
    print("Postal ballots imported:", import_postal_ballots(postal_xml))
    print("Tally:", tally())
    print("Winner:", winner())
    print("Alice %:", vote_percent("Alice"))
    print("Bob votes counted directly:", count_for("Bob", ballots))
    print("Turnout %:", turnout())
    print("Announcements:", announce())
    print("Receipt:", voters["V2"]["receipt"])

if __name__ == "__main__":
    main()
