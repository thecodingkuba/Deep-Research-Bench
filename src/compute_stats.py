import pandas as pd
import matplotlib.pyplot as plt
import json
import os

# Set pandas display options to show full text
pd.set_option('display.max_colwidth', None)  
pd.set_option('display.width', 1000)        


def print_best_results(dataframe, count=3):
    """
    Print the best results from the dataframe.
    """
    print(dataframe.sort_values('overall_score').head(3)[['query', 'overall_score']])

def print_worst_results(dataframe, count=3):
    """
    Print the worst results from the dataframe.
    """
    print(dataframe.sort_values('overall_score', ascending=False).head(3)[['query', 'overall_score']])

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
    # print the columns for debugging
    print("Available columns:", result_df.columns.tolist())
   
    # Create language-specific subset dataframes
    english_df = result_df[result_df["language"] == "en"]
    english_df = english_df.drop(columns=["language"])
    chinese_df = result_df[result_df["language"] == "zh"]
    chinese_df = chinese_df.drop(columns=["language"])    
    # Create topic specific dataframes
    



    # Run your existing analysis
    # analyze_scores(result_df, "ENGLISH", color='blue', filename='all_scores_distribution.png')
    # print_best_results(result_df, count=5)   
    # print_worst_results(result_df, count=5)  

if __name__ == "__main__":
    main()








