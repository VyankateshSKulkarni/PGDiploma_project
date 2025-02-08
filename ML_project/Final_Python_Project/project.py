from flask import Flask, request, jsonify, render_template
import pandas as pd

# Load the datasets
df = pd.read_csv('numeric.csv')
similarity_df = pd.read_csv('similarity_matrix.csv')
summarized_df = pd.read_csv('sent_sum.csv', encoding='latin1')

# Flask application
app = Flask(__name__)

# Function to extract mobile sentiment
def mobile_sentiment(user_input, summarized_df):
    if user_input not in summarized_df['Mobile_Name'].unique():
        return None, None
    index = summarized_df[summarized_df['Mobile_Name'] == user_input].index[0]
    positive_score = summarized_df.loc[index, 'Positive_score']
    negative_score = summarized_df.loc[index, 'Negative_score']
    summary = summarized_df.loc[index, 'Summary']
    if summary == "No reviews available for this mobile":
        return None, None
    return positive_score, negative_score

# Function to extract mobile features
def mobile_feature(user_input, summarized_df):
    if user_input not in summarized_df['Mobile_Name'].unique():
        return "Mobile name not found."
    index = summarized_df[summarized_df['Mobile_Name'] == user_input].index[0]
    return summarized_df.loc[index, 'Information']

# Function to extract mobile summary
def mobile_summary(user_input, summarized_df):
    if user_input not in summarized_df['Mobile_Name'].unique():
        return "Mobile name not found."
    index = summarized_df[summarized_df['Mobile_Name'] == user_input].index[0]
    return summarized_df.loc[index, 'Summary']


def recommend_mobile(user_input, df, similarity_df):
    if user_input not in df['Mobile_name'].unique():
        return []
    index = df[df['Mobile_name'] == user_input].index[0]
    similarity_scores = similarity_df.iloc[index]
    # Ensure indices are integers
    top_indices = similarity_scores.nlargest(6).index[1:]  # Exclude the first as it's the same mobile
    top_indices = top_indices.astype(int)  # Convert to integers

    recommendations = []
    for idx in top_indices:
        if idx < len(df):
            mobile_name = df.iloc[idx]['Mobile_name']
            # Fetch link from 'sent_sum.csv' (ensure href column exists in summarized_df)
            link = summarized_df.loc[summarized_df['Mobile_Name'] == mobile_name, 'href'].values
            href = link[0] if len(link) > 0 else "#"
            recommendations.append({'name': mobile_name, 'link': href})
    return recommendations


# Route for the home page
@app.route('/')
def index():
    mobile_names = summarized_df['Mobile_Name'].unique().tolist()
    return render_template('index1.html', mobile_names=mobile_names)

# Route to handle data retrieval for a selected mobile
@app.route('/get-mobile-data')
def get_mobile_data():
    mobile_name = request.args.get('mobile')
    if mobile_name not in summarized_df['Mobile_Name'].unique():
        return jsonify({'error': 'Mobile name not found'})

    # Extract features, summary, and sentiment
    features = mobile_feature(mobile_name, summarized_df)
    summary = mobile_summary(mobile_name, summarized_df)
    positive_score, negative_score = mobile_sentiment(mobile_name, summarized_df)
    sentiment = {
        'Positive': positive_score if positive_score is not None else "N/A",
        'Negative': negative_score if negative_score is not None else "N/A"
    }

    # Get recommendations
    recommendations = recommend_mobile(mobile_name, df, similarity_df)

    return jsonify({
        'features': features,
        'summary': summary,
        'sentiment': sentiment,
        'recommendations': recommendations
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
