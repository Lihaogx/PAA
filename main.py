import os
import csv
from agent import LegislatorAgent
import sys
import argparse
# os.environ["http_proxy"] = "http://localhost:7890"
# os.environ["https_proxy"] = "http://localhost:7890"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profiles_path', type=str, required=True, help='Path to profiles that need prediction')
    args = parser.parse_args()

    profiles_path = args.profiles_path 
    committee_matches_file_path = 'PAA/data/committee_match.json'  # No need to modify
    caucus_matches_file_path = 'PAA/data/caucus_match.json'  # No need to modify  
    output_csv_file = 'PAA/results/20-result433.csv'  # Path to save results

    # Open CSV file for writing
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Selected profile file', 'Bill Name', 'Personal Prediction', 'Real Result', 'Bill Number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Iterate through all JSON files
        files = [f for f in os.listdir(profiles_path) if
                 os.path.isfile(os.path.join(profiles_path, f)) and f.endswith('.json')]

        for profile_file in files:
            profile_path = os.path.join(profiles_path, profile_file)

            # Create LegislatorAgent instance
            agent = LegislatorAgent(profile_path)

            # Get unused voting records
            unused_voting_records = agent.profile_data.get("UnusedVotingRecords", [])
            if not unused_voting_records:
                continue  # Skip files with no unused voting records

            for new_bill in unused_voting_records:
                bill_info = {
                    "Bill Number": new_bill.get("Bill Number"),
                    "Bill Name": new_bill.get("Bill Name"),
                    "Summary": new_bill.get("Summary", ""),
                    "Democrat_Yea": new_bill.get("Democrat_Yea", ""),
                    "Democrat_Nay": new_bill.get("Democrat_Nay", ""),
                    "Republican_Yea": new_bill.get("Republican_Yea", ""),
                    "Republican_Nay": new_bill.get("Republican_Nay", "")
                }

                try:
                    # Prediction based on personal profile
                    personal_prediction_output = agent.decision_coT(
                        bill_info,
                        committee_matches_file_path=committee_matches_file_path,
                        caucus_matches_file_path=caucus_matches_file_path,
                        include_committee_info=True  # True or False to decide whether to include committee info
                    )

                    # Write to CSV file
                    writer.writerow({
                        'Selected profile file': profile_file,
                        'Bill Name': bill_info.get('Bill Name', ''),
                        'Personal Prediction': personal_prediction_output.get('personal_prediction', ''),
                        'Real Result': personal_prediction_output.get('real_result', ''),
                        'Bill Number': bill_info.get('Bill Number', ''),
                    })
                except ValueError as e:
                    continue  # Skip current bill and continue to next one

            print(f"Processed file: {profile_file}")


if __name__ == "__main__":
    main()
