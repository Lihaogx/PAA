# prompts
# 职务信息
# 职务信息
def public_office_prompts(name, public_office):
    positions_summary = ""
    for office_title, office_info in public_office.items():
        incumbent_status = office_info.get("Incumbent", "Unknown")

        district_info = office_info.get("District Info", {})
        district_info_summary = (
            f"Median household income: {district_info.get('Median household income', 'Unknown')}\n"
            f"Distribution: {district_info.get('Distribution', 'Unknown')}\n"
            f"Population: {district_info.get('Population', 'Unknown')}\n"
            f"Ethnicity: {district_info.get('Ethnicity', 'Unknown')}"
        )

        positions_summary += (
            f"Position: {office_title}\n"
            f"Current status: {incumbent_status}\n"
            f"District Information:\n{district_info_summary}\n\n"
        )

    return [
        {
            "role": "system",
            "content": f"You are now {name}. Here is a summary of your public office roles and responsibilities. "
                       f"this public office information is about your political career,this is the most important"
                       f"on your decision."
        },
        {
            "role": "user",
            "content": (
                f"{name}, you have held the following positions:\n\n"
                f"{positions_summary}\n\n"

            )
        }
    ]


# 个人信息
def personal_details_prompts(name, personal_details):
    born = personal_details.get("Born", "Unknown")
    political_party = personal_details.get("Political party", "Unknown")
    spouse = personal_details.get("Spouse", "Unknown")
    children = personal_details.get("Children", "Unknown")

    return [
        {
            "role": "system",
            "content": f"You are now {name}. Here is a summary of your personal details."
                       f"personal details provide interpretability for your decisions"
        },
        {
            "role": "user",
            "content": (
                f"Personal Information:\n"
                f"Born: {born}\n"
                f"Political Party: {political_party}\n"
                f"Spouse: {spouse}\n"
                f"Children: {children}\n"
            )
        }
    ]


# 法案信息
def bills_prompts(name, sponsored_bills, cosponsored_bills, voting_records, new_bill):
    # Combine all relevant bills and voting records
    all_bills = sponsored_bills + cosponsored_bills

    # Build the prompts to guide the decision-making process
    prompts = [
        {
            "role": "system",
            "content": f"Now you are {name}, and here is the summary of the bills you sponsor, cosponsor, and your "
                       f"previous voting records."
                       f"your legislative records reflect the political field you have previously focused on."
        },
        {
            "role": "user",
            "content": "Here is a summary of the relevant bills and your voting history ."

        }
    ]

    # Add sponsored and cosponsored bills information
    for bill in all_bills:
        bill_number = bill.get("Bill Number", "Unknown")
        bill_name = bill.get("Bill Name", "Unknown")
        subject_areas = bill.get("Subject Areas", "Unknown")
        prompts.append(
            {
                "role": "user",
                "content": (
                    f"Bill Number: {bill_number}\n"
                    f"Bill Name: {bill_name}\n"
                    f"Subject Areas: {subject_areas}\n"
                )
            }
        )

    # Add previous voting records
    for record in voting_records:
        bill_number = record.get("Bill Number", "Unknown")
        bill_name = record.get("Bill Name", "Unknown")
        vote = record.get("Vote", "Unknown")
        summary = record.get("Summary", "No summary provided")

        prompts.append(
            {
                "role": "user",
                "content": (
                    f"Voting Record:\n"
                    f"Bill Number: {bill_number}\n"
                    f"Bill Name: {bill_name}\n"
                    f"Vote: {vote}\n"
                    f"Summary: {summary}\n\n"
                )
            }
        )

    new_bill_number = new_bill.get("Bill Number", "Unknown")
    new_bill_name = new_bill.get("Bill Name", "Unknown")
    new_bill_subject_areas = new_bill.get("Subject Areas", "Unknown")
    new_bill_summary = new_bill.get("Summary", "No summary provided")
    new_bill_D_yea = new_bill.get("Democrat_Yea", "Unknown")
    new_bill_R_yea = new_bill.get("Republican_Yea", "Unknown")
    new_bill_D_nay = new_bill.get("Democrat_Nay", "Unknown")
    new_bill_R_nay = new_bill.get("Republican_Nay", "Unknown")

    prompts.append(
        {
            "role": "user",
            "content": (
                f"New Bill to be considered:\n"
                f"Bill Number: {new_bill_number}\n"
                f"Bill Name: {new_bill_name}\n"
                f"Subject Areas: {new_bill_subject_areas}\n"
                f"Summary: {new_bill_summary}\n"
                f"Democrat vote yea percentage on this bill:{new_bill_D_yea}\n"
                f"Republican vote yea percentage on this bill:{new_bill_R_yea}\n"
                f"Democrat vote nay percentage on this bill:{new_bill_D_nay}\n"
                f"Republican vote nay percentage on this bill:{new_bill_R_nay}\n"
                f"Referring to the voting situation of your party."
                f"This is an important factor to guide you to make decision."

            )
        }
    )

    return prompts


# 委员会主要成员信息
def committee_and_voting_prompts(bill_info):
    # Extract committee and caucus information
    committee_info = bill_info.get('Committee', {})
    caucus_info = bill_info.get('Caucus', {})

    # Committee details
    committee_name = committee_info.get('Committee', 'Unknown Committee')
    committee_chair = committee_info.get('Chair', 'Unknown Chair')
    committee_ranking_member = committee_info.get('Ranking Member', 'Unknown Ranking Member')

    # Generate committee prompt
    committee_prompt = (
        f"Committee information is an important factor for the bill. Here are some details about the committee:\n"
        f"- **Committee**: {committee_name}\n"
        f"- **Chair**: {committee_chair}\n"
        f"- **Ranking Member**: {committee_ranking_member}\n\n"
        f"Consider how the committee's composition might influence your decision on the bill.\n\n"
    )

    # Add committee voting records
    chair_voting_records = committee_info.get('Chair Voting Records', [])
    ranking_member_voting_records = committee_info.get('Ranking Member Voting Records', [])

    # Generate voting records for committee members
    voting_prompts = []
    for record in chair_voting_records:
        name = record.get('First Name', 'Unknown Name')
        vote = record.get('Vote', 'No Vote Recorded')
        voting_prompt = (
            f"For the bill, the Chair's voting record is as follows:\n"
            f"- **Member**: {name}\n"
            f"- **Vote**: {vote}\n\n"
            f"Consider how this vote might impact your decision.\n"
        )
        voting_prompts.append(voting_prompt)

    for record in ranking_member_voting_records:
        name = record.get('First Name', 'Unknown Name')
        vote = record.get('Vote', 'No Vote Recorded')
        voting_prompt = (
            f"For the bill, the Ranking Member's voting record is as follows:\n"
            f"- **Member**: {name}\n"
            f"- **Vote**: {vote}\n\n"
            f"Consider how this vote might impact your decision.\n"
        )
        voting_prompts.append(voting_prompt)

    # Caucus details
    caucus_name = caucus_info.get('Caucus', 'Unknown Caucus')
    caucus_members = caucus_info.get('Members', [])

    # Generate caucus prompt
    caucus_prompt = (
        f"Caucus information is another important factor for the bill. Here are some details about the caucus:\n"
        f"- **Caucus**: {caucus_name}\n"
        f"- **Members**: {', '.join(caucus_members)}\n\n"
        f"Consider how the caucus's position might influence your decision on the bill.\n\n"
    )

    # Add caucus voting records
    caucus_voting_records = caucus_info.get('Caucus Voting Records', [])

    # Generate voting records for caucus members
    for record in caucus_voting_records:
        name = record.get('First Name', 'Unknown Name')
        vote = record.get('Vote', 'No Vote Recorded')
        voting_prompt = (
            f"For the bill, the caucus voting record is as follows:\n"
            f"- **Member**: {name}\n"
            f"- **Vote**: {vote}\n\n"
            f"Consider how these votes might impact your decision.\n"
        )
        voting_prompts.append(voting_prompt)

    # Combine committee and caucus prompts
    full_prompt = committee_prompt + "\n".join(voting_prompts) + "\n" + caucus_prompt

    return [{"role": "user", "content": full_prompt}]
