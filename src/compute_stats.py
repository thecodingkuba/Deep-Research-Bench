import pandas as pd
import matplotlib.pyplot as plt
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

    # Plot distribution - no need to reimport matplotlib.pyplot
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
    # Create dataframe of all queries
    input_queries_df = pd.read_json("data/prompt_data/query.jsonl", lines=True)
    output_scores_df = pd.read_json("results/race/midea/raw_results.jsonl", lines=True)
    output_scores_df = output_scores_df.drop(columns=["id", "prompt"])
    result_df = pd.concat([input_queries_df, output_scores_df], axis=1)
    # print the columns for DEBUGGING
    # print("Available columns:", result_df.columns.tolist())
   
    # Create "language" specific subset dataframes
    english_df = result_df[result_df["language"] == "en"]
    chinese_df = result_df[result_df["language"] == "zh"]
    # Create "topic" specific dataframes
    science_df = result_df[result_df["topic"] == "Science & Technology"]
    finance_df = result_df[result_df["topic"] == "Finance & Business"]
    software_df = result_df[result_df["topic"] == "Software Development"]
    health_df = result_df[result_df["topic"] == "Health"]
    # Dictionary to navigate dataframes
    topic_dfs = {
        "ALL": (result_df, "ALL SCORES", "blue", "all_scores_distribution.png"),
        "ENG": (english_df, "ENGLISH SCORES", "green", "english_scores_distribution.png"),
        "CHI": (chinese_df, "CHINESE SCORES", "red", "chinese_scores_distribution.png"),
        "SCI": (science_df, "SCIENCE SCORES", "purple", "science_scores_distribution.png"),
        "FIN": (finance_df, "FINANCE SCORES", "orange", "finance_scores_distribution.png"),
        "SOFT": (software_df, "SOFTWARE SCORES", "cyan", "software_scores_distribution.png"),
        "HEALTH": (health_df, "HEALTH SCORES", "magenta", "health_scores_distribution.png"),
    }
    # CHANGE THIS TO CHANGE WHAT IS BEING ANALYZED
    key = topic_dfs["ALL"]

    # for topic in topic_dfs:
    #     analyze_scores(topic_dfs[topic][0], topic_dfs[topic][1], color=topic_dfs[topic][2], filename=topic_dfs[topic][3])

 
    # analyze_scores(key[0], key[1], color=key[2], filename=key[3])
    # print_best_results(key[0], count=4)   
    # print_worst_results(key[0], count=4)  

if __name__ == "__main__":
    main()







