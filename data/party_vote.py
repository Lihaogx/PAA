import os
import json
import pandas as pd


class VotingRecordProcessor:
    def __init__(self, profile_folder, vote_index_file, output_folder):
        self.profile_folder = profile_folder
        self.vote_index_file = vote_index_file
        self.output_folder = output_folder
        # 确保输出文件夹存在
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def load_profiles(self):
        profiles = []
        for filename in os.listdir(self.profile_folder):
            if filename.endswith(".json"):
                file_path = os.path.join(self.profile_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    profiles.append((filename, data))
        return profiles

    def find_matching_rows(self, bill_number):
        vote_index_df = pd.read_csv(self.vote_index_file)
        matching_rows = vote_index_df[vote_index_df['Description'].str.contains(bill_number, na=False)]
        return matching_rows

    def process_profiles(self):
        profiles = self.load_profiles()
        for filename, profile in profiles:
            unused_voting_records = profile.get("UnusedVotingRecord", [])
            all_matching_rows = pd.DataFrame()

            for record in unused_voting_records:
                bill_number = record.get("Bill Number", "")
                if bill_number:
                    matching_rows = self.find_matching_rows(bill_number)
                    if not matching_rows.empty:
                        all_matching_rows = pd.concat([all_matching_rows, matching_rows])

            if not all_matching_rows.empty:
                output_file = os.path.join(self.output_folder, filename.replace(".json", ".csv"))
                all_matching_rows.to_csv(output_file, index=False)
                print(f"Saved matching records for {filename} to {output_file}")


if __name__ == "__main__":
    profile_folder = r"E:\PycharmProjects\Legislators\data\profiles\new_profiles"
    vote_index_file = r"E:\PycharmProjects\Legislators\data\vote_index.csv"
    output_folder = r"E:\PycharmProjects\Legislators\data\output"

    processor = VotingRecordProcessor(profile_folder, vote_index_file, output_folder)
    processor.process_profiles()


class VotingStatsProcessor:
    def __init__(self, csv_folder, votes_folder, output_folder):
        self.csv_folder = csv_folder
        self.votes_folder = votes_folder
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def process_files(self):
        for filename in os.listdir(self.csv_folder):
            if filename.endswith(".csv"):
                csv_file_path = os.path.join(self.csv_folder, filename)
                self.process_csv_file(csv_file_path)

    def process_csv_file(self, csv_file_path):
        df = pd.read_csv(csv_file_path)
        if 'Filename' not in df.columns:
            print(f"File {csv_file_path} does not have a 'Filename' column.")
            return

        for index, row in df.iterrows():
            vote_filename = row['Filename']
            vote_file_path = os.path.join(self.votes_folder, vote_filename)
            if os.path.exists(vote_file_path):
                vote_stats = self.get_vote_stats(vote_file_path)
                for party in ["Democrat", "Republican"]:
                    if party in vote_stats:
                        df.at[index, f"{party}_Yea"] = vote_stats[party]['Yea']
                        df.at[index, f"{party}_Nay"] = vote_stats[party]['Nay']
                    else:
                        df.at[index, f"{party}_Yea"] = 0
                        df.at[index, f"{party}_Nay"] = 0
            else:
                print(f"Vote file {vote_file_path} does not exist.")

        # 删除全零数据行
        df = df[(df['Democrat_Yea'] != 0) | (df['Democrat_Nay'] != 0) |
                (df['Republican_Yea'] != 0) | (df['Republican_Nay'] != 0)]

        output_file_path = os.path.join(self.output_folder, os.path.basename(csv_file_path))
        df.to_csv(output_file_path, index=False)
        print(f"Processed file saved to {output_file_path}")

    def get_vote_stats(self, vote_file_path):
        vote_df = pd.read_csv(vote_file_path, skiprows=[0])
        if 'party' not in vote_df.columns or 'vote' not in vote_df.columns:
            print(f"Vote file {vote_file_path} does not have 'party' or 'vote' columns.")
            return {}

        vote_stats = {}
        parties = vote_df['party'].unique()
        for party in ["Democrat", "Republican"]:
            if party in parties:
                party_votes = vote_df[vote_df['party'] == party]
                total_votes = len(party_votes)
                if total_votes == 0:
                    vote_stats[party] = {'Yea': 0, 'Nay': 0}
                else:
                    yea_votes = len(party_votes[party_votes['vote'] == 'Yea']) / total_votes
                    nay_votes = len(party_votes[party_votes['vote'] == 'Nay']) / total_votes
                    vote_stats[party] = {'Yea': yea_votes, 'Nay': nay_votes}
            else:
                vote_stats[party] = {'Yea': 0, 'Nay': 0}
        return vote_stats


if __name__ == "__main__":
    csv_folder = r"E:\PycharmProjects\Legislators\data\output"
    votes_folder = r"E:\PycharmProjects\Legislators\data\votes"
    output_folder = r"E:\PycharmProjects\Legislators\data\vote"

    processor = VotingStatsProcessor(csv_folder, votes_folder, output_folder)
    processor.process_files()


#

class CSVCleaner:
    def __init__(self, csv_folder, output_folder):
        self.csv_folder = csv_folder
        self.output_folder = output_folder
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def process_files(self):
        # 遍历 CSV 文件夹中的所有文件
        for csv_filename in os.listdir(self.csv_folder):
            if csv_filename.endswith(".csv"):
                csv_file_path = os.path.join(self.csv_folder, csv_filename)
                self.clean_csv(csv_file_path)

    def clean_csv(self, csv_file_path):
        # 读取 CSV 文件
        df = pd.read_csv(csv_file_path)
        if 'Description' not in df.columns:
            print(f"File {csv_file_path} does not have a 'Description' column.")
            return

        # 函数：检查是否需要删除
        def should_remove(description):
            if pd.isna(description):
                return False
            # 提取第一个冒号之前的内容
            before_colon = description.split(':', 1)[0]
            # 检查是否包含单词 'to' 或 'On'
            return 'to' in before_colon or 'On' in before_colon

        # 删除需要删除的行
        cleaned_df = df[~df['Description'].apply(should_remove)]

        # 保存更新后的 CSV 文件
        output_file_path = os.path.join(self.output_folder, os.path.basename(csv_file_path))
        cleaned_df.to_csv(output_file_path, index=False)
        print(f"Processed file saved to {output_file_path}")


if __name__ == "__main__":
    csv_folder = r"E:\PycharmProjects\Legislators\data\vote"
    output_folder = r"E:\PycharmProjects\Legislators\data\vote00"

    cleaner = CSVCleaner(csv_folder, output_folder)
    cleaner.process_files()


class CsvProcessor:
    def __init__(self, csv_folder, output_folder):
        self.csv_folder = csv_folder
        self.output_folder = output_folder

    def process_files(self):
        # 确保输出文件夹存在
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # 遍历 CSV 文件夹中的所有文件
        for csv_filename in os.listdir(self.csv_folder):
            if csv_filename.endswith(".csv"):
                csv_file_path = os.path.join(self.csv_folder, csv_filename)
                self.process_csv_file(csv_file_path)

    def process_csv_file(self, csv_file_path):
        df = pd.read_csv(csv_file_path)

        # 确保需要的列存在
        if 'Description' not in df.columns or 'Time' not in df.columns:
            print(f"Missing 'Description' or 'Time' column in file: {csv_file_path}")
            return

        # 提取 Description 列中的法案编号（冒号之前的内容）
        df['Bill_Number'] = df['Description'].apply(self.extract_bill_number)

        # 去掉无效的法案编号
        df = df[df['Bill_Number'].notna()]

        # 将 Time 列转换为 datetime 类型
        df['Time'] = pd.to_datetime(df['Time'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')

        # 依据 'Bill_Number' 进行分组，并保留每组中时间最晚的行
        latest_df = df.loc[df.groupby('Bill_Number')['Time'].idxmax()]

        # 删除临时列
        latest_df = latest_df.drop(columns=['Bill_Number'])

        # 保存到新的 CSV 文件
        output_file_path = os.path.join(self.output_folder, os.path.basename(csv_file_path))
        latest_df.to_csv(output_file_path, index=False)
        print(f"Processed file saved to: {output_file_path}")

    def extract_bill_number(self, description):
        """ 提取第一个冒号之前和开头的短杠加空格之后的法案编号 """
        if pd.isna(description):
            return None
        try:
            before_colon = description.split(':', 1)[0]
            # 提取短杠和空格之后的内容
            bill_number = before_colon.split('- ', 1)[-1]
            return bill_number.strip()
        except IndexError:
            return None


if __name__ == "__main__":
    csv_folder = r"E:\PycharmProjects\Legislators\data\vote00"
    output_folder = r"E:\PycharmProjects\Legislators\data\vote00"

    processor = CsvProcessor(csv_folder, output_folder)
    processor.process_files()


class ProfileUpdater:
    def __init__(self, csv_folder, profile_folder):
        self.csv_folder = csv_folder
        self.profile_folder = profile_folder

    def extract_bill_data(self, csv_file_path):
        """ 从 CSV 文件中提取法案编号及其投票数据 """
        df = pd.read_csv(csv_file_path)
        bill_data = {}

        if 'Description' in df.columns:
            for _, row in df.iterrows():
                description = row['Description']
                bill_number = self.extract_bill_number(description)
                if bill_number:
                    bill_data[bill_number] = {
                        'Democrat_Yea': row.get('Democrat_Yea', 0),
                        'Democrat_Nay': row.get('Democrat_Nay', 0),
                        'Republican_Yea': row.get('Republican_Yea', 0),
                        'Republican_Nay': row.get('Republican_Nay', 0)
                    }
        return bill_data

    def extract_bill_number(self, description):
        """ 提取第一个冒号之前和开头的短杠加空格之后的法案编号 """
        if pd.isna(description):
            return None
        try:
            before_colon = description.split(':', 1)[0]
            # 提取短杠和空格之后的内容
            bill_number = before_colon.split('- ', 1)[-1]
            return bill_number.strip()
        except IndexError:
            return None

    def update_profiles(self):
        # 遍历 CSV 文件夹中的所有文件
        for csv_filename in os.listdir(self.csv_folder):
            if csv_filename.endswith(".csv"):
                csv_file_path = os.path.join(self.csv_folder, csv_filename)
                bill_data = self.extract_bill_data(csv_file_path)

                profile_filename = csv_filename.replace('.csv', '.json')
                profile_file_path = os.path.join(self.profile_folder, profile_filename)
                self.update_profile_with_csv_data(profile_file_path, bill_data)

    def update_profile_with_csv_data(self, profile_file_path, bill_data):
        """ 更新 JSON 文件中的投票记录 """
        if not os.path.exists(profile_file_path):
            print(f"Profile file not found: {profile_file_path}")
            return

        with open(profile_file_path, 'r', encoding='utf-8') as file:
            profile_data = json.load(file)

        if 'UnusedVotingRecords' not in profile_data:
            print(f"No 'UnusedVotingRecords' field in profile file: {profile_file_path}")
            return

        for record in profile_data['UnusedVotingRecords']:
            bill_number = record.get('Bill Number')
            if bill_number in bill_data:
                record.update(bill_data[bill_number])

        # 保存更新后的 JSON 文件
        with open(profile_file_path, 'w', encoding='utf-8') as file:
            json.dump(profile_data, file, indent=4)
        print(f"Updated profile file: {profile_file_path}")


if __name__ == "__main__":
    csv_folder = r"E:\PycharmProjects\Legislators\data\vote00"
    profile_folder = r"E:\PycharmProjects\Legislators\data\profiles\new_profiles"

    updater = ProfileUpdater(csv_folder, profile_folder)
    updater.update_profiles()
