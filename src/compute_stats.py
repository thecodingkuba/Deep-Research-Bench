import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
import seaborn as sns
import json
import os

# Set pandas display options to show full text
pd.set_option('display.max_colwidth', None)  
pd.set_option('display.width', 1000)        

def print_best_results(dataframe, count=3):
    """
    Print the best results from the dataframe with better formatting.
    """
    best_results = dataframe.sort_values('overall_score', ascending=False).head(count)
    
    print("\n" + "=" * 80)
    print(f"BEST {count} RESULTS")
    print("=" * 80)
    
    for i, (_, row) in enumerate(best_results.iterrows(), 1):
        print(f"\nRESULT #{i} ID.{row['id']} :")
        print(f"  Score: {row['overall_score']:.4f}")
        print(f"  Prompt: ")
        # Indent the prompt text and wrap long lines   
        prompt_lines = row['prompt'].split('\n')
        for line in prompt_lines:
            # Wrap long lines at 70 characters
            for j in range(0, len(line), 70):
                print(f"    {line[j:j+70]}")
        print("-" * 80)
    
    return best_results

def print_worst_results(dataframe, count=3):
    """
    Print the worst results from the dataframe with better formatting.
    """
    worst_results = dataframe.sort_values('overall_score', ascending=True).head(count)
    
    print("\n" + "=" * 80)
    print(f"WORST {count} RESULTS")
    print("=" * 80)
    
    for i, (_, row) in enumerate(worst_results.iterrows(), 1):
        print(f"\nRESULT #{i} ID.{row['id']} :")
        print(f"  Score: {row['overall_score']:.4f}")
        print(f"  Prompt: ")
        # Indent the prompt text and wrap long lines
        prompt_lines = row['prompt'].split('\n')
        for line in prompt_lines:
            # Wrap long lines at 70 characters
            for j in range(0, len(line), 70):
                print(f"    {line[j:j+70]}")
        print("-" * 80)
    
    return worst_results

def find_length_bias(dataframe):
    """
    Analyze the length bias in the dataframe.
    """
    pearson_corr, pearson_p = pearsonr(dataframe["output_length"], dataframe['overall_score'])  
    spearman_corr, spearman_p = spearmanr(dataframe["output_length"], dataframe['overall_score'])

    print("\nLength Bias Analysis:")
    print(f"Pearson Correlation: {pearson_corr:.4f}, p-value: {pearson_p:.4f}")
    print(f"Spearman Correlation: {spearman_corr:.4f}, p-value: {spearman_p:.4f}")
    
    # Create a scatterplot for Pearson with regression line
    sns.lmplot(data=dataframe, x='output_length', y='overall_score', ci=None)
    plt.title('Output Length vs. Score (Pearson Correlation)')
    plt.xlabel('Word Count')
    plt.ylabel('Score')
    plt.show()

     # Create a scatterplot for Spearman with regression line
    sns.lmplot(data=dataframe, x='output_length', y='overall_score', ci=None)
    plt.title('Output Length vs. Score (Spearman Correlation)')
    plt.xlabel('Word Count')
    plt.ylabel('Score')
    plt.show()

def analyze_scores(dataframe, title, color='blue', filename=None):
    """    
    Parameters:
    dataframe (DataFrame): The pandas DataFrame containing 'overall_score'
    title (str): The title prefix for the analysis (e.g., 'ALL', 'ENGLISH', 'CHINESE')
    color (str): The color for the histogram bars
    filename (str, optional): The filename to save the plot, if None, won't save
    """
    # Compute statistics
    stats = dataframe['overall_score'].describe()
    print(f"\n{title} PROMPTS STATISTICS:")
    print(stats)

    plt.figure(figsize=(10, 6))
    plt.hist(dataframe['overall_score'], bins=15, alpha=0.7, color=color)
    plt.title(f'Distribution of {title} Scores')
    plt.xlabel('Overall Score')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)
    
    # Add vertical lines for mean and median
    plt.axvline(dataframe['overall_score'].mean(), color='red', linestyle='dashed', linewidth=2, 
               label=f'Mean: {dataframe["overall_score"].mean():.2f}')
    plt.axvline(dataframe['overall_score'].median(), color='green', linestyle='dashed', linewidth=2,
               label=f'Median: {dataframe["overall_score"].median():.2f}')
    plt.legend()
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename)
    plt.show()
    
    return stats

def main():
    # Create a master dataframe
    input_queries_df = pd.read_json("data/prompt_data/query.jsonl", lines=True)
    output_scores_df = pd.read_json("results/race/midea/raw_results.jsonl", lines=True)
    output_len = pd.read_json("data/test_data/raw_data/midea.jsonl", lines=True)["article"].apply(len)
    # check consistency between prompts and results
    assert len(output_scores_df) == len(input_queries_df), "Mismatch in number of queries and results"
    for i in range(len(input_queries_df)):
        assert output_scores_df.iloc[i]["prompt"] == input_queries_df.iloc[i]["prompt"], f"Prompt mismatch at id {i + 1}"
    output_scores_df = output_scores_df.drop(columns=["id", "prompt"])
    result_df = pd.concat([input_queries_df, output_scores_df], axis=1)
    result_df["output_length"] = output_len

 
    # print the columns for DEBUGGING
    # print("Available columns:", result_df.columns.tolist())
   
    # Create "language" and "topic" specific subset dataframes
    english_df = result_df[result_df["language"] == "en"]
    chinese_df = result_df[result_df["language"] == "zh"]
    science_df = result_df[result_df["topic"] == "Science & Technology"]
    finance_df = result_df[result_df["topic"] == "Finance & Business"]
    software_df = result_df[result_df["topic"] == "Software Development"]
    health_df = result_df[result_df["topic"] == "Health"]
    
    # Dictionary to navigate dataframes
    analysis_groups = {
        "ALL": (result_df, "ALL SCORES", "blue", "data/stats_data/all_scores_distribution.png"),
        "ENG": (english_df, "ENGLISH SCORES", "green", "data/stats_data/english_scores_distribution.png"),
        "CHI": (chinese_df, "CHINESE SCORES", "red", "data/stats_data/chinese_scores_distribution.png"),
        "SCI": (science_df, "SCIENCE SCORES", "purple", "data/stats_data/science_scores_distribution.png"),
        "FIN": (finance_df, "FINANCE SCORES", "orange", "data/stats_data/finance_scores_distribution.png"),
        "SOFT": (software_df, "SOFTWARE SCORES", "cyan", "data/stats_data/software_scores_distribution.png"),
        "HEALTH": (health_df, "HEALTH SCORES", "magenta", "data/stats_data/health_scores_distribution.png"),
    }
    # CHANGE THIS TO CHANGE WHAT IS BEING ANALYZED
    key = analysis_groups["ALL"]

    # *********ALL TOPICS**********
    # for topic in analysis_groups:
    #     analyze_scores(analysis_groups[topic][0], analysis_groups[topic][1], color=analysis_groups[topic][2], filename=analysis_groups[topic][3])

    # *********ONE TOPIC**********
    # analyze_scores(key[0], key[1], color=key[2], filename=key[3])

    # *********WORST/BEST CASES**********
    # print_best_results(key[0], count=4)   
    # # print_worst_results(key[0], count = 4)  

    # *****MISCELLANEOUS PRINTING SPACE******
    # print(result_df[result_df["id"] == 74])

    # Find length bias
    # find_length_bias(key[0])
    # print("DONE")


if __name__ == "__main__":
    main()







