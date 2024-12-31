def generate_quality_summary(df, scores_df):
    try:
        # Initialize the HTML content with a link to the external CSS
        html_content = []
        html_content.append("""
        <link rel="stylesheet" href="Data_Validation\\dataquaclms\\Gqcls.css">

        <div class="container">
            <div class="metrics-container">
        """)

        # Generate HTML content for each metric card
        for metric in scores_df.columns:
            columns_passing = scores_df[scores_df[metric] >= 80].index.tolist()
            passing_percentage = (len(columns_passing) / len(scores_df)) * 100

            html_content.append(f"""
            <div class="metric-card">
                <div class="metric-title">{metric}</div>
                <div class="passing-percentage">{passing_percentage:.2f}% Passing</div>
            """)

            if columns_passing:
                html_content.append("<ul class='columns-list'>")
                for col in columns_passing:
                    html_content.append(f"<li>{col}</li>")
                html_content.append("</ul>")
            else:
                html_content.append("<p class='no-columns'>No columns passed this metric.</p>")

            html_content.append("</div>")  # Closing metric-card

        # Close containers
        html_content.append("""
            </div> <!-- Closing metrics-container -->
        </div> <!-- Closing container -->
        """)

        return "\n".join(html_content)

    except Exception as e:
        print(f"Error generating quality summary report: {e}")
        return ""
