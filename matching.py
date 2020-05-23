import pandas as pd
import numpy as np
import csv

## Check in common identities they care about
def get_common_identities(row):
    common = row['Q47'].split(',')
    common_qs = []
    if 'None' in common:
        return []
    if 'Ability Status' in common:
        common_qs.append('Q41')

    if 'Ethnicity/Race' in common:
        common_qs.append('Q37')
    if 'Dietary Restrictions' in common:
        common_qs.append('Q42')
    if 'First Generation and/or Limited Income Status' in common:
        common_qs.append('Q39')
    if 'Gender Identity' in common:
        common_qs.append('Q36')
    if 'Religion' in common:
        common_qs.append('Q40')
    if 'Sexual Orientation' in common:
        common_qs.append('Q38')
    return common_qs

## Check Intended major, minors etc.
def get_certifications(row):
    school = row['Q11']
    major = row['Q12']
    minor = row['Q13']
    cert = row['Q14']

    return [school, major, minor, cert]

## Nervous
def get_nervous(row):

    return row['Q19']

## Frequency
def get_frequencies(row):

    summer_freq = row['Q33']

    sem_freq = row['Q34']

    return [summer_freq, sem_freq]

## Kind of relationship
def get_relationship(row):

    return row['Q35']
## Saturday Night
def get_saturday_night(row):

    return row['Q26']
## Drinking
def get_drinking(row):

    return row['Q21']
## Hobbies
def get_hobbies(row):

    return row['Q23'].split(',')
## Interests - Clubs, Academic Programs
def get_primary_interests(row):

    clubs = row['Q15'].split(',')

    academic = row['Q18'].split(',')

    clubs.append(academic)

    return clubs
## Interesets - Affiliations, Sports
def get_secondary_interests(row):

    affiliations = row['Q16'].split(',')

    sports = row['Q17'].split(',')

    affiliations.append(sports)

    return affiliations

def get_identity_score(mentee, mentor):

    relevant_identities = get_common_identities(mentee)
    score = 0
    for i in relevant_identities:
        if mentee[i] == mentor[i]:
            score += 100
        else:
            score -= 50
    
    return score

def get_major_scores(mentee, mentor):

    mentee_certs = get_certifications(mentee)
    mentor_certs = get_certifications(mentor)
    score = 0
    if mentee_certs[0] == mentor_certs[0]:
        score += 20
    if mentee_certs[1] == mentor_certs[1]:
        score += 30
    if mentee_certs[2] == mentor_certs[2]:
        score += 10
    if mentee_certs[3] == mentor_certs[3]:
        score += 10

    return score

def get_nervous_score(mentee, mentor):

    mentee_nervous = get_nervous(mentee)
    mentor_nervous = get_nervous(mentor)

    if mentee_nervous == mentor_nervous:
        return 20
    else:
        return 0

def get_freq_score(mentee, mentor):

    mentee_freqs = get_frequencies(mentee)
    mentor_freqs = get_frequencies(mentor)
    score = 0

    for i in range(len(mentee_freqs)):
        if mentee_freqs[i]==mentor_freqs[i]:
            score += 20
    
    return score

def get_relationship_score(mentee, mentor):
    mentee_rel = get_relationship(mentee)
    mentor_rel = get_relationship(mentor)

    if mentee_rel == mentor_rel:
        return 20
    
    return 0

def get_drinking_score(mentee, mentor):
    mentee_drink = get_drinking(mentee)
    mentor_drink = get_drinking(mentor)

    if mentee_drink == mentor_drink:
        return 20
    return 0

def get_hobby_score(mentee, mentor):
    mentee_hobbies = get_hobbies(mentee)
    mentor_hobbies = get_hobbies(mentor)
    score = 0
    for hobby in mentee_hobbies:
        if hobby in mentor_hobbies:
            score += 5
    
    return score

def get_interest_scores(mentee, mentor):
    mentee_primary_interest = get_primary_interests(mentee)
    mentee_secondary_interest = get_secondary_interests(mentee)

    mentor_primary_interest = get_primary_interests(mentor)
    mentor_secondary_interest = get_secondary_interests(mentor)

    score = 0

    for men_p_int in mentee_primary_interest:
        if men_p_int in mentor_primary_interest:
            score += 6
    
    for men_s_int in mentee_secondary_interest:
        if men_s_int in mentor_secondary_interest:
            score += 3

    return score

def get_saturday_score(mentee, mentor):
    mentee_sat = get_saturday_night(mentee)
    mentor_sat = get_saturday_night(mentor)

    if mentee_sat == mentor_sat:
        return 20

    return 0

def get_timezone(row):
    
    f = row['Q9'].split(':')
    
    s = f[0].split('GMT')[1].strip()
    if s == '':
        return 0
    
    return int(s)

def get_timezone_diff(mentee, mentor):
    mentee_timezone = get_timezone(mentee)
    mentor_timezone = get_timezone(mentor)

    return abs(mentee_timezone - mentor_timezone)

def get_matching_score(mentee, mentor):

    time_diff = get_timezone_diff(mentee, mentor)

    if time_diff > 3:
        return 0

    score = 0

    score += get_identity_score(mentee, mentor)
    score += get_major_scores(mentee, mentor)
    score += get_nervous_score(mentee, mentor)
    score += get_freq_score(mentee, mentor)
    score += get_relationship_score(mentee, mentor)
    score += get_drinking_score(mentee, mentor)
    score += get_hobby_score(mentee, mentor)
    score += get_interest_scores(mentee, mentor)
    score += get_saturday_score(mentee, mentor)

    return score

def match():
    mentors = pd.read_csv('mentor.csv')
    mentors.fillna('', inplace = True)
    mentors = mentors.to_dict('index')
    mentees = pd.read_csv('mentee.csv')
    mentees.fillna('', inplace = True)
    mentees = mentees.to_dict('index')
    num_mentors = len(mentors)
    num_mentees = len(mentees)

    scores = np.zeros((num_mentees, num_mentors))
    for i, mentee in enumerate(mentees):
        
        for j, mentor in enumerate(mentors):
            
            scores[j, i] = get_matching_score(mentees[mentee], mentors[mentor])
    pairs = []
    print(scores)
    for i in range(num_mentees):
        max_val = np.amax(scores[:,i])
        max_loc = np.where(scores[:,i] == max_val)
        j = max_loc[0][0]
        
        pairs.append({'mentor': mentors[j], 'mentee': mentees[i]})
        
        scores[:][j] = -1000
        

    return pairs

def write_csv_out(pairs):
    with open('matchings.csv', 'w', newline='') as csv_out:
        writer = csv.writer(csv_out, delimiter=' ')
        writer.writerow(['Mentor Name', 'Mentor Email', 'Mentee Name', 'Mentee Email'])
        for p in pairs:
            mentor_name = p['mentor']['FirstName'] + ' ' + p['mentor']['LastName']
            mentor_email = p['mentor']['NetIDEmail']
            mentee_name = p['mentee']['FirstName'] + ' ' + p['mentee']['LastName']
            mentee_email = p['mentee']['NetIDEmail']
            data = [mentor_name, mentor_email, mentee_name, mentee_email]
            writer.writerow(data)

write_csv_out(match())