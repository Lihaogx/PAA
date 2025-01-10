# PAA
This is the code for the paper **"Political Actor Agent: Simulating Legislative System for Roll Call Votes Prediction with Large Language Models"**.

## Environment
PAA requires API keys for large language models. If you want to use local models (like llama, deepseek), please make sure you have the corresponding models running.

## File Structure
### agent
The agent folder contains PAA's code:
 - agent/decision_pathway.py Uses LLM to analyze committees and caucuses corresponding to different bills
 - agent/legislator_agent.py Code for PAA's legislator agents
 - agent/prompts.py Prompts used by PAA

### data
The data folder contains PAA's data, including experiments mentioned in the paper:
 - data/profiles Different profile types used by PAA
 - data/district District information
 - data/votes Voting data
 - data/caucus_committee.py Adds leader agents to legislator profiles
 - data/wiki.json Legislator wiki information
 - data/caucus_committee.csv Analysis results from agent/decision_pathway.py
 - data/caucus_data.json Caucus information
 - data/committee_data.json Committee information
 - data/caucus_match.json Results of caucus-bill analysis matching
 - data/committee_match.json Results of committee-bill analysis matching
 - data/name_process.py Used for ablation experiments, replaces legislator names

## Running
After processing the profiles files, run main.py in the following format:

```bash
python main.py --profiles_path data/profiles/20-profiles433
```

## Citation
If you find our paper helpful, please cite:
```
@article{li2024political,
  title={Political Actor Agent: Simulating Legislative System for Roll Call Votes Prediction with Large Language Models},
  author={Li, Hao and Gong, Ruoyuan and Jiang, Hao},
  journal={arXiv preprint arXiv:2412.07144},
  year={2024}
}
```