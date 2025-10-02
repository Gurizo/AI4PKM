AI Directives: Read and Execute Precisely

1. Output Format & Style:

Your entire output must be ONLY the content between the [START OF REPORT] and [END OF REPORT] markers.

DO NOT output any text or commentary before [START OF REPORT] or after [END OF REPORT].

Use HTML for layout and tables to ensure maximum compatibility and a professional appearance.

Report Title: The main title must be large and centered using an <h1> tag.

Section Headers: Use <h3> tags for main section headers (e.g., "Executive Summary").

Sub-Section Headers: Use <h4> tags for sub-sections (e.g., "Purpose and Goals").

2. Data Sourcing & Inference Mandate:

Primary Source First: Always try to use the specific .csv, .xlsx, or .json file mentioned.

Mandatory Inference as Fallback: If a primary source file is not found, you MUST infer the information by analyzing all other available context (raw_data/GobiData/, processed_data/, press_clippings/).

Cite Your Source: When providing an inferred or estimated piece of information, you MUST state the source of your analysis (e.g., "(Source: Estimated based on crowd photo analysis.)").

Narrative Over Empty Tables: If a section's primary data is entirely missing, replace the table with a short narrative paragraph explaining that the data was unavailable.

[START OF REPORT]

<div style="font-family: Arial, sans-serif; margin: 2em;">

<h1 style="text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px;">Event Report: [Event Name]</h1>

<p><strong>Presented by:</strong> [Organizer Name]




<strong>Date of Event:</strong> [Date]




<strong>Location:</strong> [Venue/Location]




<strong>Date of Submission:</strong> [Date of Report Submission]</p>

<hr>

Executive Summary
[AI: Write a 1-paragraph summary. Start with the most impactful results (e.g., "Drawing an estimated 500+ attendees and supporting 22 local vendors..."). Then, briefly describe the event's purpose, key highlights, and its overall value to the community.]

<hr>

1. Event Overview
<h4>1.1. Purpose and Goals</h4>
[AI: Summarize the event&#39;s purpose from &#39;event_details.txt&#39;. If unavailable, infer the purpose from other sources, citing the source.]

<h4>1.2. Program & Activities</h4>
[AI: Present the &#39;event_schedule.csv&#39; data in a clean, readable HTML table.]

<h4>1.3. Partners, Sponsors, and Key Contributors</h4>
[AI: From &#39;partners_list.csv&#39;, categorize all organizations under the subheadings: &lt;strong&gt;Financial Sponsors&lt;/strong&gt;, &lt;strong&gt;Community Partners&lt;/strong&gt;, &lt;strong&gt;Marketplace Operator&lt;/strong&gt;, and &lt;strong&gt;Vendors &amp; Artists&lt;/strong&gt;.]

<hr>

2. Attendance & Demographics
<h4>2.1. Participation Metrics</h4>
[AI: Populate from &#39;event_metrics.csv&#39;. If unavailable, provide a narrative summary, including an estimated &#39;Total Attendees&#39; based on photo analysis.]

<h4>2.2. Participant Demographics</h4>
[AI: Summarize &#39;participant_survey.json&#39;. If unavailable, provide a qualitative analysis of crowd diversity based on event photos.]

<hr>

3. Financial Report
[AI: Populate from 'financial_log.xlsx'. If unavailable, replace this section with a paragraph explaining the missing data.]

<hr>

4. Event Feedback & Analysis
<h4>4.1. Event Highlights & Lowlights</h4>
<ul>
<li><strong>Highlights:</strong> [AI: Describe 2-3 significant positive moments from Gobi transcripts and photos, supported by quotes or detailed descriptions.]</li>
<li><strong>Lowlights:</strong> [AI: This is MANDATORY. Analyze Gobi transcripts for 1-2 distinct challenges (e.g., attendee confusion, logistical issues) and support with quotes.]</li>
</ul>

<h4>4.2. Recommendations for Future Events</h4>
[AI: For each &quot;Lowlight,&quot; provide a corresponding, actionable recommendation.]

<h4>4.3. Volunteer Feedback</h4>
[AI: Summarize &#39;volunteer_feedback.txt&#39;. If unavailable, synthesize feedback from volunteer conversations in Gobi transcripts.]

<hr>

5. Community & Economic Impact
<h4>5.1. Local Economic Effect</h4>
<ul>
<li><strong>Local Artists & Vendors Supported:</strong> [AI: Count unique artists/vendors from &#39;partners_list.csv&#39;.]</li>
<li><strong>RPD (Random Play Dance) Participation:</strong> [AI: Describe participation qualitatively, citing press clippings and photo analysis if &#39;activity_attendance.csv&#39; is missing.]</li>
<li><strong>Song-by-Song Counter:</strong> [AI: Summarize &#39;rpd_song_log.csv&#39; if it exists, using an HTML table.]</li>
</ul>

<h4>5.2. Promotion & Visibility</h4>
<ul>
<li><strong>Press & Media Coverage:</strong> [AI: List publication names from &#39;./press_clippings/&#39; in a clean bulleted list.]</li>
</ul>

<hr>

6. Safety & Operations
<h4>6.1. On-site Safety</h4>
<ul>
<li><strong>Safety Incidents:</strong> [AI: Summarize &#39;incident_log.txt&#39; and scan Gobi transcripts for safety keywords. State &quot;No safety or medical incidents were reported&quot; if none are found.]</li>
</ul>

<hr>

7. Conclusion: Value to the City of Bellevue
[AI: Write a 2-3 paragraph analysis of the event's value, synthesizing key data and qualitative insights to build a compelling narrative.]

<hr>

8. Appendices
<p><em>[Manual Task: This section lists all supporting documents.]</em></p>
<ol>
<li><strong>Financials:</strong> Copies of all invoices, receipts, and proofs of expenditure.</li>
<li><strong>Marketing Materials:</strong> Copies of flyers, posters, and digital ads.</li>
<li><strong>Site Map:</strong> Layout of the event grounds.</li>
<li><strong>Press Clippings:</strong> Copies of all media articles.</li>
</ol>

</div>

[END OF REPORT]