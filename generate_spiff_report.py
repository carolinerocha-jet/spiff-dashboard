#!/usr/bin/env python3
"""
SPIFF Ticket Report Generator
Auto-generates weekly SPIFF ticket dashboard and Slack report
Run this script every Monday morning to update the dashboard

Requirements:
  pip install pandas plotly

Usage:
  python generate_spiff_report.py /path/to/tickets_export.csv
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import sys
import os

def generate_dashboard(csv_path, output_html='spiff_dashboard.html', output_slack='slack_report.txt'):
    """Generate HTML dashboard and Slack report from SPIFF CSV export"""
    
    # Load data
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    df['Created At'] = pd.to_datetime(df['Created At'], utc=True)
    df['Resolved At'] = pd.to_datetime(df['Resolved At'], utc=True)
    
    # Current date (when script runs)
    current_time = pd.Timestamp.now(tz='UTC')
    
    # Last week = Previous Monday to Sunday
    last_week_monday = current_time - pd.Timedelta(days=current_time.weekday() + 7)
    last_week_sunday = last_week_monday + pd.Timedelta(days=6)
    last_week_num = last_week_monday.isocalendar()[1]
    
    # Calculate No of Days
    df['No of Days'] = np.nan
    for idx, row in df.iterrows():
        if pd.notna(row['Resolved At']) and pd.notna(row['Created At']):
            time_diff = row['Resolved At'] - row['Created At']
            df.at[idx, 'No of Days'] = round(time_diff.total_seconds() / (24 * 3600), 2)
    
    # --- METRICS ---
    last_week_tickets = df[(df['Created At'] >= last_week_monday) & (df['Created At'] <= last_week_sunday)]
    num_last_week = len(last_week_tickets)
    last_week_resolved = last_week_tickets[last_week_tickets['Resolved At'].notna()]
    avg_sla_last_week = last_week_resolved['No of Days'].mean() if len(last_week_resolved) > 0 else 0
    
    current_quarter = (current_time.month - 1) // 3 + 1
    quarter_start = pd.Timestamp(year=current_time.year, month=(current_quarter-1)*3+1, day=1, tz='UTC')
    quarter_tickets = df[df['Created At'] >= quarter_start]
    num_this_quarter = len(quarter_tickets)
    quarter_resolved = quarter_tickets[quarter_tickets['Resolved At'].notna()]
    avg_sla_this_quarter = quarter_resolved['No of Days'].mean() if len(quarter_resolved) > 0 else 0
    
    # --- WEEKLY TREND ---
    weeks_data = []
    for i in range(6, 0, -1):
        w_start = last_week_monday - pd.Timedelta(days=7*i)
        w_end = w_start + pd.Timedelta(days=6)
        week_tickets = df[(df['Created At'] >= w_start) & (df['Created At'] <= w_end)]
        week_resolved = week_tickets[week_tickets['Resolved At'].notna()]
        
        weeks_data.append({
            'label': f"{w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}",
            'count': len(week_tickets),
            'avg_sla': week_resolved['No of Days'].mean() if len(week_resolved) > 0 else 0
        })
    
    # --- LAST 3 MONTHS ---
    three_months_ago = current_time - pd.Timedelta(days=90)
    last_3m_df = df[df['Created At'] >= three_months_ago]
    
    owner_stats = last_3m_df[last_3m_df['Assigned To'].notna()].groupby('Assigned To').agg({
        'Ticket Number': 'count',
        'No of Days': 'mean'
    }).rename(columns={'Ticket Number': 'Count', 'No of Days': 'Avg SLA'})
    owner_stats = owner_stats.sort_values('Count', ascending=False).head(8)
    
    status_counts = last_3m_df['Status'].value_counts()
    
    # --- SLACK REPORT ---
    open_df = df[df['Resolved At'].isna()].copy()
    open_df['Days Open'] = (current_time - open_df['Created At']).dt.total_seconds() / (24 * 3600)
    open_df['Days Open'] = open_df['Days Open'].round(0).astype(int)
    
    new_gt_3_days = open_df[(open_df['Status'] == 'New') & (open_df['Days Open'] > 3)]
    in_progress_gt_7_days = open_df[(open_df['Status'] == 'In Progress') & (open_df['Days Open'] > 7)]
    oldest_tickets = open_df.nlargest(3, 'Days Open')
    
    def format_assignee(assignee):
        if pd.isna(assignee):
            return "Unassigned"
        assignee = str(assignee).replace('"', '')
        if ',' in assignee:
            names = [name.strip() for name in assignee.split(',')]
            return ' '.join([f"@{name.replace(' ', '').lower()}" for name in names])
        else:
            return f"@{assignee.replace(' ', '').lower()}"
    
    slack_report = f""":ticket: SPIFF Ticket Report – Week {last_week_num} ({last_week_monday.strftime('%b %d')} - {last_week_sunday.strftime('%b %d')})

:rotating_light: ACTION REQUIRED:

{len(new_gt_3_days)} tickets in NEW status > 3 days
{len(in_progress_gt_7_days)} tickets in IN PROGRESS status > 7 days


:clock-stopwatch: Oldest Open Tickets:
"""
    
    for i, (idx, row) in enumerate(oldest_tickets.iterrows(), 1):
        slack_report += f"""{i}. #{int(row['Ticket Number'])}: {row['Subject']}
→ Status: {row['Status']}
→ Assigned: {format_assignee(row['Assigned To'])}
→ Open for {row['Days Open']} days

"""
    
    with open(output_slack, 'w', encoding='utf-8') as f:
        f.write(slack_report)
    
    # --- HTML DASHBOARD ---
    fig = make_subplots(
        rows=3, cols=4,
        row_heights=[0.15, 0.4, 0.45],
        column_widths=[0.25, 0.25, 0.25, 0.25],
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "xy", "colspan": 4, "secondary_y": True}, None, None, None],
            [{"type": "xy", "colspan": 2}, None, {"type": "xy"}, None]
        ],
        subplot_titles=("", "", "", "",
                        "Weekly Ticket Volume & SLA Trend (Last 6 Weeks)",
                        "Total Tickets by Owner (Top 8, Last 3 Months)", "", "Status (Last 3 Months)"),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    # Metrics
    metrics_data = [
        (num_last_week, "# Last Week", "orange", 1),
        (f"{avg_sla_last_week:.2f}", "AVG. SLA Last Week", "green", 2),
        (f"{avg_sla_this_quarter:.2f}", "AVG. SLA This Quarter", "blue", 3),
        (num_this_quarter, "# This Quarter", "orange", 4)
    ]
    
    for value, label, color, col in metrics_data:
        fig.add_trace(go.Indicator(
            mode="number",
            value=float(value) if isinstance(value, int) else float(value.replace(',', '')),
            number={'font': {'size': 50, 'color': color}, 'valueformat': '.0f' if isinstance(value, int) else '.2f'},
            title={'text': label, 'font': {'size': 14, 'color': 'gray'}},
        ), row=1, col=col)
    
    # Weekly trend
    x_labels = [w['label'] for w in weeks_data]
    ticket_counts = [w['count'] for w in weeks_data]
    sla_values = [w['avg_sla'] for w in weeks_data]
    
    fig.add_trace(go.Scatter(
        x=x_labels, y=ticket_counts,
        mode='lines+markers+text',
        name='Tickets per Week',
        line=dict(color='#FF8C42', width=3),
        marker=dict(size=10),
        text=ticket_counts,
        textposition='top center',
        textfont=dict(size=11, color='#FF8C42'),
    ), row=2, col=1)
    
    fig.add_trace(go.Scatter(
        x=x_labels, y=sla_values,
        mode='lines+markers+text',
        name='Average SLA',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=10, symbol='square'),
        text=[f'{v:.2f}' for v in sla_values],
        textposition='top center',
        textfont=dict(size=11, color='#4CAF50'),
        yaxis='y2'
    ), row=2, col=1, secondary_y=True)
    
    fig.update_xaxes(title_text="", row=2, col=1)
    fig.update_yaxes(title_text="Tickets per Week", title_font=dict(color='#FF8C42', size=13), 
                     tickfont=dict(color='#FF8C42'), row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Average SLA (Days)", title_font=dict(color='#4CAF50', size=13), 
                     tickfont=dict(color='#4CAF50'), row=2, col=1, secondary_y=True)
    
    # Owner chart
    owner_names = [name.replace('"', '') for name in owner_stats.index.tolist()]
    owner_counts = owner_stats['Count'].values.tolist()
    owner_slas = owner_stats['Avg SLA'].values.tolist()
    
    fig.add_trace(go.Bar(
        y=owner_names[::-1],
        x=owner_counts[::-1],
        orientation='h',
        marker=dict(color='#FF8C42'),
        text=[f"{count}<br>Avg: {sla:.2f}d" for count, sla in zip(owner_counts[::-1], owner_slas[::-1])],
        textposition='outside',
        showlegend=False
    ), row=3, col=1)
    
    fig.update_xaxes(title_text="Total Tickets", row=3, col=1)
    
    # Status chart
    status_names = status_counts.index.tolist()
    status_vals = status_counts.values.tolist()
    colors_status = {'Resolved': '#4CAF50', 'New': '#FF6B6B', 'In Progress': '#FFD93D'}
    bar_colors = [colors_status.get(s, '#CCCCCC') for s in status_names]
    
    fig.add_trace(go.Bar(
        x=status_names,
        y=status_vals,
        marker=dict(color=bar_colors),
        text=status_vals,
        textposition='outside',
        showlegend=False
    ), row=3, col=3)
    
    fig.update_yaxes(title_text="Number of Tickets", row=3, col=3)
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f"<b>SPIFF Ticket Report - Week {last_week_num} ({last_week_monday.strftime('%b %d')} - {last_week_sunday.strftime('%b %d')})</b>",
            font=dict(size=24),
            x=0.5,
            xanchor='center'
        ),
        height=1000,
        showlegend=True,
        legend=dict(x=0.4, y=0.65, orientation='h'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif")
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
    
    fig.write_html(output_html, config={'displayModeBar': True, 'displaylogo': False})
    
    print(f"✓ Dashboard generated: {output_html}")
    print(f"✓ Slack report generated: {output_slack}")
    print(f"  Week {last_week_num}: {last_week_monday.strftime('%b %d')} - {last_week_sunday.strftime('%b %d')}")
    
    return output_html, output_slack


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_spiff_report.py <path_to_csv>")
        print("Example: python generate_spiff_report.py /data/tickets_export.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)
    
    generate_dashboard(csv_path)
