"""
Affinity Analysis Script for TRS Engine Core
Analyzes and visualizes results from emotional_log CSV files
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import glob
import os

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def load_latest_csv(log_dir="../Logs"):
    """Load the most recent emotional_log CSV file"""
    csv_files = glob.glob(f"{log_dir}/emotional_log_*.csv")
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {log_dir}/")
    
    latest_file = max(csv_files, key=os.path.getmtime)
    print(f"[INFO] Loading: {latest_file}")
    return pd.read_csv(latest_file), latest_file


def summary_statistics(df):
    """Display summary statistics"""
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    
    print(f"\nTotal Records: {len(df)}")
    print(f"Unique Candidates: {df['name'].nunique()}")
    print(f"Unique Vacancies: {df['vacancy'].nunique()}")
    
    print("\n--- Score Statistics ---")
    print(df[['match_score', 'penalty', 'adjusted_score']].describe())
    
    print("\n--- Emotional State Distribution ---")
    print(df['emotional_state'].value_counts())
    
    print("\n--- Top 5 Best Matches ---")
    top_matches = df.nlargest(5, 'adjusted_score')[['name', 'vacancy', 'adjusted_score', 'emotional_state']]
    print(top_matches.to_string(index=False))
    
    print("\n--- Bottom 5 Worst Matches ---")
    worst_matches = df.nsmallest(5, 'adjusted_score')[['name', 'vacancy', 'adjusted_score', 'emotional_state']]
    print(worst_matches.to_string(index=False))


def plot_score_distribution(df, save_path=None):
    """Plot distribution of match scores"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Match Score Distribution
    axes[0].hist(df['match_score'], bins=10, color='skyblue', edgecolor='black')
    axes[0].set_title('Match Score Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Match Score')
    axes[0].set_ylabel('Frequency')
    axes[0].axvline(df['match_score'].mean(), color='red', linestyle='--', label=f'Mean: {df["match_score"].mean():.2f}')
    axes[0].legend()
    
    # Penalty Distribution
    axes[1].hist(df['penalty'], bins=10, color='salmon', edgecolor='black')
    axes[1].set_title('Penalty Distribution', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Penalty')
    axes[1].set_ylabel('Frequency')
    axes[1].axvline(df['penalty'].mean(), color='red', linestyle='--', label=f'Mean: {df["penalty"].mean():.2f}')
    axes[1].legend()
    
    # Adjusted Score Distribution
    axes[2].hist(df['adjusted_score'], bins=15, color='lightgreen', edgecolor='black')
    axes[2].set_title('Adjusted Score Distribution', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Adjusted Score')
    axes[2].set_ylabel('Frequency')
    axes[2].axvline(df['adjusted_score'].mean(), color='red', linestyle='--', label=f'Mean: {df["adjusted_score"].mean():.2f}')
    axes[2].legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
    
    plt.close()


def plot_emotional_analysis(df, save_path=None):
    """Analyze scores by emotional state"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Box plot: Adjusted Score by Emotional State
    emotional_order = ['Negative', 'Neutral', 'Positive']
    colors = {'Negative': 'lightcoral', 'Neutral': 'lightgray', 'Positive': 'lightgreen'}
    
    sns.boxplot(data=df, x='emotional_state', y='adjusted_score', 
                order=emotional_order, palette=colors, ax=axes[0, 0])
    axes[0, 0].set_title('Adjusted Score by Emotional State', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Emotional State')
    axes[0, 0].set_ylabel('Adjusted Score')
    
    # Count plot: Emotional State Distribution
    sns.countplot(data=df, x='emotional_state', order=emotional_order, 
                  palette=colors, ax=axes[0, 1])
    axes[0, 1].set_title('Emotional State Distribution', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Emotional State')
    axes[0, 1].set_ylabel('Count')
    
    # Violin plot: Match Score by Emotional State
    sns.violinplot(data=df, x='emotional_state', y='match_score', 
                   order=emotional_order, palette=colors, ax=axes[1, 0])
    axes[1, 0].set_title('Match Score Distribution by Emotional State', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Emotional State')
    axes[1, 0].set_ylabel('Match Score')
    
    # Average scores by emotional state
    avg_scores = df.groupby('emotional_state')[['match_score', 'penalty', 'adjusted_score']].mean()
    avg_scores = avg_scores.reindex(emotional_order)
    avg_scores.plot(kind='bar', ax=axes[1, 1], color=['steelblue', 'orange', 'green'])
    axes[1, 1].set_title('Average Scores by Emotional State', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Emotional State')
    axes[1, 1].set_ylabel('Score')
    axes[1, 1].legend(['Match Score', 'Penalty', 'Adjusted Score'])
    axes[1, 1].tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
    
    plt.close()


def plot_candidate_heatmap(df, save_path=None):
    """Create a heatmap of adjusted scores: candidates vs vacancies"""
    pivot_table = df.pivot_table(values='adjusted_score', 
                                  index='name', 
                                  columns='vacancy', 
                                  aggfunc='mean')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='RdYlGn', 
                center=0, cbar_kws={'label': 'Adjusted Score'})
    plt.title('Candidate-Vacancy Match Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Vacancy', fontsize=12)
    plt.ylabel('Candidate', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
    
    plt.close()


def plot_correlation_matrix(df, save_path=None):
    """Plot correlation matrix of numerical features"""
    numerical_cols = ['match_score', 'penalty', 'adjusted_score']
    corr_matrix = df[numerical_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, linewidths=1)
    plt.title('Feature Correlation Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[SAVED] {save_path}")
    
    plt.close()


def export_insights(df, output_path="../Logs/reports/insights.txt"):
    """Export key insights to a text file"""
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("TRS ENGINE CORE - DATA INSIGHTS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Total Records: {len(df)}\n")
        f.write(f"Unique Candidates: {df['name'].nunique()}\n")
        f.write(f"Unique Vacancies: {df['vacancy'].nunique()}\n\n")
        
        f.write("--- Emotional State Distribution ---\n")
        f.write(df['emotional_state'].value_counts().to_string() + "\n\n")
        
        f.write("--- Average Scores by Emotional State ---\n")
        avg_by_emotion = df.groupby('emotional_state')[['match_score', 'penalty', 'adjusted_score']].mean()
        f.write(avg_by_emotion.to_string() + "\n\n")
        
        f.write("--- Top 10 Best Matches ---\n")
        top_10 = df.nlargest(10, 'adjusted_score')[['name', 'vacancy', 'adjusted_score', 'emotional_state']]
        f.write(top_10.to_string(index=False) + "\n\n")
        
        f.write("--- Candidates with Negative Emotional State ---\n")
        negative_candidates = df[df['emotional_state'] == 'Negative'][['name', 'vacancy', 'adjusted_score']].drop_duplicates('name')
        f.write(negative_candidates.to_string(index=False) + "\n\n")
        
        f.write("--- Key Recommendations ---\n")
        f.write("1. Focus on candidates with adjusted_score > 0\n")
        f.write("2. Provide support to candidates with Negative emotional state\n")
        f.write("3. Review penalty factors for low-scoring matches\n")
        f.write("4. Consider expanding job requirements to improve match rates\n")
    
    print(f"[SAVED] Insights exported to: {output_path}")


def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("TRS ENGINE CORE - AFFINITY ANALYSIS")
    print("="*80)
    
    try:
        # Load data
        df, csv_path = load_latest_csv()
        
        # Create output directory for visualizations
        output_dir = "../Logs/plots"
        os.makedirs(output_dir, exist_ok=True)
        
        # Display summary statistics
        summary_statistics(df)
        
        # Generate visualizations
        print("\n[INFO] Generating visualizations...")
        
        plot_score_distribution(df, f"{output_dir}/score_distributions.png")
        plot_emotional_analysis(df, f"{output_dir}/emotional_analysis.png")
        plot_candidate_heatmap(df, f"{output_dir}/candidate_heatmap.png")
        plot_correlation_matrix(df, f"{output_dir}/correlation_matrix.png")
        
        # Export insights
        export_insights(df)
        
        print("\n" + "="*80)
        print("[SUCCESS] Analysis complete!")
        print(f"[INFO] Visualizations saved to: {output_dir}/")
        print(f"[INFO] Insights report saved to: ../Logs/reports/")
        print("="*80 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("[INFO] Run emotional_inference_engine.py first to generate data.\n")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}\n")


if __name__ == "__main__":
    main()

