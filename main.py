import os
import csv
from agent import LegislatorAgent, DecisionPathway

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"


def main():
    folder_path = r"E:\PycharmProjects\Legislators\data\profiles\20-profiles622"  # 需要预测的Profiles路径
    committee_matches_file_path = r"E:\PycharmProjects\Legislators\data\committee_match.json"  # 不用改动
    caucus_matches_file_path = r"E:\PycharmProjects\Legislators\data\caucus_match.json"  # 不用改动
    output_csv_file = r"E:\PycharmProjects\Legislators\result\20-result622.csv"  # 结果保存路径

    # 打开 CSV 文件以进行写入
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Selected profile file', 'Bill Name', 'Personal Prediction', 'Real Result', 'Bill Number']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # 遍历所有 JSON 文件
        files = [f for f in os.listdir(folder_path) if
                 os.path.isfile(os.path.join(folder_path, f)) and f.endswith('.json')]

        for profile_file in files:
            profile_path = os.path.join(folder_path, profile_file)

            # 创建 LegislatorAgent 实例
            agent = LegislatorAgent(profile_path)

            # 获取未使用的投票记录
            unused_voting_records = agent.profile_data.get("UnusedVotingRecords", [])
            if not unused_voting_records:
                continue  # 跳过没有未使用投票记录的文件

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
                    # 基于个人 profile 的预测
                    personal_prediction_output = agent.decision_coT(
                        bill_info,
                        committee_matches_file_path=committee_matches_file_path,
                        caucus_matches_file_path=caucus_matches_file_path,
                        include_committee_info=True  # 或 False 来决定是否包含委员会信息
                    )

                    # 写入 CSV 文件
                    writer.writerow({
                        'Selected profile file': profile_file,
                        'Bill Name': bill_info.get('Bill Name', ''),
                        'Personal Prediction': personal_prediction_output.get('personal_prediction', ''),
                        'Real Result': personal_prediction_output.get('real_result', ''),
                        'Bill Number': bill_info.get('Bill Number', ''),
                    })
                except ValueError as e:
                    continue  # 跳过当前法案，继续下一个

            print(f"Processed file: {profile_file}")


if __name__ == "__main__":
    main()
