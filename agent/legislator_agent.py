import openai
import os
import json
from agent.prompts import public_office_prompts, personal_details_prompts, bills_prompts, committee_and_voting_prompts

openai.api_key = os.getenv("OPENAI_API_KEY")
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


class LegislatorAgent:
    def __init__(self, profile_path):
        self.profile_path = profile_path
        self.profile_data = self.load_profile()
        self.history = []
        self.client = openai.OpenAI(api_key=openai.api_key)

    def load_profile(self):
        with open(self.profile_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def load_matches(self, matches_file_path):
        with open(matches_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def find_bill_info(self, bill_name, committee_matches, caucus_matches):
        # Search in both committee and caucus matches
        for matches_data in [committee_matches, caucus_matches]:
            for item in matches_data:
                if item.get('Bill Name') == bill_name:
                    return item
        return None

    def decision_coT(self, bill, committee_matches_file_path, caucus_matches_file_path, include_committee_info=True):
        # Load matches data
        committee_matches = self.load_matches(committee_matches_file_path)
        caucus_matches = self.load_matches(caucus_matches_file_path)

        # Find bill info
        bill_info = self.find_bill_info(bill.get('Bill Name', ''), committee_matches, caucus_matches)
        if not bill_info:
            raise ValueError("Bill information not found in matches files.")

        name = self.profile_data.get('Profile', {}).get('Name', 'Unknown')
        public_office_prompt = public_office_prompts(
            name,
            self.profile_data.get('Profile', {}).get('Public Office', {})
        )

        personal_details_prompt = personal_details_prompts(
            name,
            self.profile_data.get('Profile', {}).get('Personal Details', {}).get('Personal details', {})
        )

        bills_prompt = bills_prompts(
            name,
            self.profile_data.get('SponsoredBills', []),
            self.profile_data.get('CosponsoredBills', []),
            self.profile_data.get('VotingRecord', []),
            new_bill=bill
        )

        # Generate committee and caucus prompts if needed
        committee_and_caucus_prompt = committee_and_voting_prompts(bill_info) if include_committee_info else []

        all_prompts = public_office_prompt + personal_details_prompt + bills_prompt + committee_and_caucus_prompt

        format_prompt = (
            "Consider all above factors may make influence on your decision, vote on the bill."
            f"Remember, you now are not AI but a legislator, so you must vote on this bill and tell reason."
            "Provide a prediction in the format below. Do not include additional text.Format:"
            "bill: {bill_name}\n"
            "personal prediction: {personal_prediction}\n"
            "real result: {real_result}\n\n"
        ).format(
            bill_name=bill.get("Bill Name", "Unknown"),
            personal_prediction="",
            real_result=""
        )

        # Combine all prompts and the format prompt
        messages = [{"role": "user", "content": "\n".join([item['content'] for item in all_prompts] + [format_prompt])}]
        self.history.extend(messages)

        # Make the API call to get the completion
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        response = completion.choices[0].message.content.strip()

        # Extract the prediction and reason from the response
        lines = response.split('\n')
        result = {line.split(':', 1)[0].strip(): line.split(':', 1)[1].strip() for line in lines if ':' in line}

        # Extract fields from the result
        personal_prediction = result.get('personal prediction', 'Unknown')
        reason = result.get('reason', 'No reason provided')
        real_result = self.get_real_result(bill.get("Bill Name"))

        return {
            "bill": bill.get("Bill Name", "Unknown"),
            "personal_prediction": personal_prediction,
            "real_result": real_result
        }

    def get_real_result(self, bill_name):
        unused_voting_records = []
        for file in os.listdir(os.path.dirname(self.profile_path)):
            if file.endswith('.json'):
                profile_path = os.path.join(os.path.dirname(self.profile_path), file)
                try:
                    with open(profile_path, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                        records = profile_data.get('UnusedVotingRecords', [])
                        for record in records:
                            if record.get('Bill Name') == bill_name:
                                return record.get('Vote', 'No vote recorded')
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {profile_path}")
        return 'No result found'
