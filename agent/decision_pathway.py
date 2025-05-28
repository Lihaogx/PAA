## sdjfhjfklsajfksdaf匹配
import os
import json
import openai
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
# os.environ["http_proxy"] = "http://localhost:7890"
# os.environ["https_proxy"] = "http://localhost:7890"


class DecisionPathway:
    def __init__(self, caucus_file, committee_file, profiles_folder):
        self.caucus_file = caucus_file
        self.committee_file = committee_file
        self.profiles_folder = profiles_folder
        self.client = openai.OpenAI(api_key=openai.api_key)

    def load_json(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_caucus(self, bill_name, bill_summary):
        caucus_data = self.load_json(self.caucus_file)
        if isinstance(caucus_data, dict):
            caucus_dict = caucus_data.get('Caucuses', {})
            caucus_list = list(caucus_dict.keys())
        elif isinstance(caucus_data, list):
            caucus_dict = {item.get('Caucus', ''): item for item in caucus_data}
            caucus_list = list(caucus_dict.keys())
        else:
            raise ValueError("Caucus data format is not as expected")

        prompt = (
            f"Based on the following bill information, identify which caucus it belongs to:\n\n"
            f"Bill Name: {bill_name}\n"
            f"Bill Summary: {bill_summary}\n\n"
            "Available caucuses:\n"
            f"{', '.join(caucus_list)}\n\n"
            "Please specify the most relevant caucus for this bill."
            "Format your output into:"
            "Caucus:[caucus name]\n"
            "Reason:[why you choose this caucus]"
        )

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        results = completion.choices[0].message.content.strip()
        return results

    def find_committee(self, bill_name, bill_summary):
        committee_data = self.load_json(self.committee_file)
        if not isinstance(committee_data, dict):
            raise ValueError("Committee data should be a dictionary")

        prompt = (
                "Format your output into:"
                "Committee:[committee name]\n"
                "Reason:[why you choose this committee]"
                f"Match the following bill to the most relevant committee:\n\n"
                f"Bill Name: {bill_name}\n"
                f"Bill Summary: {bill_summary}\n\n"
                "Committee Data:\n" + json.dumps(committee_data, indent=2)

        )

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        results = completion.choices[0].message.content.strip()
        return results

    def predict_decision(self, bill_info):
        bill_name = bill_info.get('Bill Name')
        bill_summary = bill_info.get('Summary', '')

        # Identify relevant caucus and committee
        caucus_prediction = self.find_caucus(bill_name, bill_summary)
        committee_prediction = self.find_committee(bill_name, bill_summary)

        # Return the predictions in a dictionary
        return {
            'Identified Caucus': self.extract_info(caucus_prediction, 'Caucus:'),
            'Identified Committee': self.extract_info(committee_prediction, 'Committee:')
        }

    def extract_info(self, text, label):
        """Extract information with specified label from text"""
        if not isinstance(text, str):
            text = str(text)  # Ensure text is a string
        pattern = rf'{label}\s*(.+)'  # Match content after the label
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ''
