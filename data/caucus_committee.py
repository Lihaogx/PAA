import json
import pandas as pd
import os


def clean_text(text):
    # Ensure value is string and clean text
    return str(text).strip().strip('"').strip()


def load_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_personal_profiles(folder_path):
    profiles = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_profile.json'):
            file_path = os.path.join(folder_path, file_name)
            profile_data = load_json_file(file_path)
            person_name = file_name.replace('_profile.json', '')
            profiles[person_name] = profile_data
    return profiles


def process_csv(csv_filename, caucus_json_filename, committee_json_filename):
    # Read CSV file
    df = pd.read_csv(csv_filename)

    # Load JSON data
    caucus_data = load_json_file(caucus_json_filename)
    committee_data = load_json_file(committee_json_filename)

    # Match caucus data
    caucus_matches = []
    for _, row in df.iterrows():
        bill_number = row['Bill Number']
        bill_name = row['Bill Name']
        caucus_name = clean_text(row['Caucus'])

        # Find matching caucus
        matched_caucus = next((item for item in caucus_data if item['Caucus'] == caucus_name), None)

        if matched_caucus:
            caucus_matches.append({
                "Bill Number": bill_number,
                "Bill Name": bill_name,
                "Caucus": matched_caucus
            })
        else:
            print(f"Caucus not found: {caucus_name}")

    # Match committee data
    committee_matches = []
    for _, row in df.iterrows():
        bill_number = row['Bill Number']
        bill_name = row['Bill Name']
        committee_name = clean_text(row['Committee'])

        # Find matching committee
        matched_committee = committee_data.get(committee_name, None)

        if matched_committee:
            committee_matches.append({
                "Bill Number": bill_number,
                "Bill Name": bill_name,
                "Committee": {
                    "Committee": committee_name,
                    "Chair": matched_committee.get("Chair"),
                    "Ranking Member": matched_committee.get("Ranking Member")
                }
            })
        else:
            print(f"Committee not found: {committee_name}")

    # Save match results to files
    save_json_file('caucus_matches.json', caucus_matches)
    save_json_file('committee_matches.json', committee_matches)


def update_committee_matches(file_path, profiles):
    committee_matches = load_json_file(file_path)
    for entry in committee_matches:
        bill_number = entry.get("Bill Number")
        committee_info = entry.get("Committee", {})
        chair_name = committee_info.get("Chair")
        ranking_member_name = committee_info.get("Ranking Member")

        for person_name in [chair_name, ranking_member_name]:
            if person_name in profiles:
                profile = profiles[person_name]
                records_fields = ['UnusedVotingRecords', 'CosponsoredBills', 'VotingRecord', 'SponsoredBills']
                for field in records_fields:
                    if field in profile:
                        for record in profile[field]:
                            if record.get("Bill Number") == bill_number:
                                if field not in entry:
                                    entry[field] = []
                                entry[field].append(record)
    save_json_file(file_path, committee_matches)


def update_caucus_matches(file_path, profiles):
    caucus_matches = load_json_file(file_path)
    for entry in caucus_matches:
        bill_number = entry.get("Bill Number")
        caucus_info = entry.get("Caucus", {})
        members = caucus_info.get("Members", [])

        for person_name in members:
            clean_person_name = person_name.split('(')[0].strip()
            if clean_person_name in profiles:
                profile = profiles[clean_person_name]
                records_fields = ['UnusedVotingRecords', 'CosponsoredBills', 'VotingRecord', 'SponsoredBills']
                for field in records_fields:
                    if field in profile:
                        for record in profile[field]:
                            if record.get("Bill Number") == bill_number:
                                if field not in entry:
                                    entry[field] = []
                                entry[field].append(record)
    save_json_file(file_path, caucus_matches)


def process_committee_json(input_file, output_file):
    # Read input JSON file
    with open(input_file, 'r') as f:
        data_list = json.load(f)

    # Process each data item
    for data in data_list:
        # Get committee chair and ranking member names
        committee_chair = data["Committee"]["Chair"]
        committee_ranking_member = data["Committee"]["Ranking Member"]

        # Initialize empty voting records
        data["Committee"]["Chair Voting Records"] = []
        data["Committee"]["Ranking Member Voting Records"] = []

        # Define fields to check
        fields_to_check = ["UnusedVotingRecords", "CosponsoredBills", "SponsoredBills", "VotingRecord"]

        # Iterate and match
        for field in fields_to_check:
            if field in data:
                records = data[field]
                updated_records = []
                for record in records:
                    first_name = record.get("First Name", "").strip()
                    last_name = record.get("Last Name", "").strip()
                    vote = record.get("Vote", "")

                    # Check if matches chair
                    if committee_chair in first_name:
                        data["Committee"]["Chair Voting Records"].append({
                            "First Name": first_name,
                            "Last Name": last_name,
                            "Vote": vote
                        })
                    # Check if matches ranking member
                    elif committee_ranking_member in first_name:
                        data["Committee"]["Ranking Member Voting Records"].append({
                            "First Name": first_name,
                            "Last Name": last_name,
                            "Vote": vote
                        })
                    else:
                        updated_records.append(record)

                # Update original field
                data[field] = updated_records

        # Delete processed records
        for field in fields_to_check:
            if field in data:
                del data[field]

    # Save processed data to new JSON file
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)


def process_caucus_json(input_file, output_file):
    # Read input JSON file
    with open(input_file, 'r') as f:
        data_list = json.load(f)

    for data in data_list:
        # Get committee name and members
        caucus_name = data["Caucus"]["Caucus"]
        caucus_members = data["Caucus"]["Members"]

        # Initialize empty voting records
        data["Caucus"]["Caucus Voting Records"] = []

        # Define fields to check
        fields_to_check = ["UnusedVotingRecords", "CosponsoredBills", "SponsoredBills", "VotingRecord"]

        # Store temporary records
        temp_records = {}

        # Iterate and collect records
        for field in fields_to_check:
            if field in data:
                records = data[field]
                for record in records:
                    first_name = record.get("First Name", "").strip()
                    last_name = record.get("Last Name", "").strip()
                    vote = record.get("Vote", "")

                    if first_name:
                        if first_name not in temp_records:
                            temp_records[first_name] = {"Last Name": "", "Vote": ""}

                        if vote:
                            temp_records[first_name]["Vote"] = vote
                        if last_name:
                            temp_records[first_name]["Last Name"] = last_name

        # Match records and fill into "Caucus Voting Records"
        for member in caucus_members:
            member_name = member.split('(')[0].strip()  # Only get name part, remove party info
            if member_name in temp_records:
                data["Caucus"]["Caucus Voting Records"].append({
                    "First Name": member_name,
                    "Last Name": temp_records[member_name]["Last Name"],
                    "Vote": temp_records[member_name]["Vote"]
                })

        # Delete processed record fields
        for field in fields_to_check:
            if field in data:
                del data[field]

    # Save processed data to new JSON file
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=4)


def main():
    personal_profiles_folder = '/home/lh/PAA/data/profiles/profiles244'
    csv_filename = 'caucus_committee.csv'
    caucus_json_filename = 'caucus_data.json'
    committee_json_filename = 'committee_data.json'
    committee_matches_file = 'committee_matches.json'
    caucus_matches_file = 'caucus_matches.json'
    committee_output_file = 'committee_match.json'
    caucus_output_file = 'caucus_match.json'

    profiles = load_personal_profiles(personal_profiles_folder)

    # Process CSV file
    process_csv(csv_filename, caucus_json_filename, committee_json_filename)

    # Update committee_matches.json and caucus_matches.json files
    update_committee_matches(committee_matches_file, profiles)
    update_caucus_matches(caucus_matches_file, profiles)
    process_committee_json(committee_matches_file, committee_output_file)
    process_caucus_json(caucus_matches_file, caucus_output_file)

    print("Committee match results saved to", committee_output_file)
    print("Caucus match results saved to", caucus_output_file)


if __name__ == "__main__":
    main()

# Read JSON file
with open('caucus_match.json', 'r') as file:
    data = json.load(file)

# Ensure data is a list
if isinstance(data, list):
    for item in data:
        # Extract party information
        members = item.get("Caucus", {}).get("Members", [])
        party_dict = {}

        for member in members:
            # Extract name and party
            name, party = member.rsplit('(', 1)
            party = party.rstrip(')')
            full_name = name.strip()
            party_dict[full_name] = party

        # Update party information in voting records
        voting_records = item.get("Caucus", {}).get("Caucus Voting Records", [])

        for record in voting_records:
            full_name = record.get("First Name", "").strip()
            if full_name in party_dict:
                record["Last Name"] = party_dict[full_name]

    # Write back to JSON file
    with open('caucus_match.json', 'w') as file:
        json.dump(data, file, indent=4)

    print("Update completed!")
else:
    print("Data read is not a list type, please check JSON file structure.")
