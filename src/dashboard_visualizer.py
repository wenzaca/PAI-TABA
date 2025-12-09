"""
Dashboard Creator
Creates a single HTML dashboard with all visualizations including:
- Data comparison widgets
- Statistical summaries
- Correlation analysis
- All 6 original visualizations
- Additional insights
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from pathlib import Path
from src.analysis_results import AnalysisResults

class DashboardVisualizer:
    def __init__(self, output_dir='output', template_path='templates/dashboard.html'):
        self.output_dir = output_dir
        self.template_path = template_path
        self.logger = logging.getLogger(__name__)
    
    def create(self, analysis_results: AnalysisResults | Dict[str, Any]) -> None:
        """
        Create comprehensive dashboard with all visualizations organized by sections
        
        Args:
            analysis_results: Either an AnalysisResults dataclass instance or a dictionary
                            with the same structure (for backward compatibility)
        """
        self.logger.info("Creating comprehensive dashboard...")
        
        # Convert to dict if AnalysisResults dataclass is provided
        if isinstance(analysis_results, AnalysisResults):
            analysis_dict = analysis_results.to_dict()
        else:
            analysis_dict = analysis_results
        
        integrated_df = analysis_dict['processed_data']['integrated']
        correlations = analysis_dict.get('correlations', {})
        trends = analysis_dict.get('trends', {})
        county_analysis = analysis_dict.get('county_analysis', {})
        
        pvp_analysis = analysis_dict.get('pollution_vs_population_analysis', {})
        pvw_analysis = analysis_dict.get('pollution_vs_water_analysis', {})
        pollution_df = analysis_dict['processed_data']['pollution']
        pvp_df = analysis_dict['processed_data'].get('pollution_vs_population', pd.DataFrame())
        
        fig = make_subplots(
            rows=9, cols=2,
            subplot_titles=(
                '1. Water Quality Trend (National Avg)',
                '2. Water Quality Rankings (Top 15)',
                '3. Water Quality Trends by County',
                '4. Water Quality Distribution (Box Plot)',
                '5. Pollution Trend (All Years 2009-2023)',
                '6. Population Growth per County (Year-over-Year)',
                '7. National Population Growth (2011, 2016, 2022)',
                '8. Population Rankings (Top 12)',
                '9. Pollution-Water Correlation',
                '10. Pollution vs Water Quality (All Counties)',
                '11. Population vs Water Quality (2022)',
                '12. Correlation Analysis',
                '13. Overall Correlation Matrix',
                '14. Estimated County Emissions (2022)',
                '15. Population-Pollution Correlation (Census Years)',
                '16. County Data Comparison Table',
                '17. Key Statistics Summary',
                '18. Data Quality & Coverage'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "box"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "heatmap"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "table"}],
                [{"type": "table"}, {"type": "table"}]
            ],
            vertical_spacing=0.04,
            horizontal_spacing=0.15
        )
        
        annual_water = integrated_df.groupby('year')['avg_quality_score'].mean()
        fig.add_trace(
            go.Scatter(
                x=annual_water.index,
                y=annual_water.values,
                mode='lines+markers',
                line=dict(color='blue', width=3),
                marker=dict(size=10),
                showlegend=False
            ),
            row=1, col=1
        )
        
        county_avg_quality = integrated_df.groupby('county')['avg_quality_score'].mean().sort_values(ascending=False).head(15)
        fig.add_trace(
            go.Bar(
                x=county_avg_quality.values,
                y=county_avg_quality.index,
                orientation='h',
                marker=dict(color=county_avg_quality.values, colorscale='Viridis'),
                text=[f'{v:.2f}' for v in county_avg_quality.values],
                textposition='auto',
                showlegend=False
            ),
            row=1, col=2
        )
        
        for county in integrated_df['county'].unique()[:8]:
            county_data = integrated_df[integrated_df['county'] == county]
            fig.add_trace(
                go.Scatter(
                    x=county_data['year'],
                    y=county_data['avg_quality_score'],
                    mode='lines+markers',
                    name=county
                ),
                row=2, col=1
            )
        
        fig.add_trace(
            go.Box(
                y=integrated_df['avg_quality_score'],
                x=integrated_df['county'],
                marker=dict(color='blue'),
                showlegend=False
            ),
            row=2, col=2
        )
        
        annual_pollution_all = pollution_df.groupby('year')['pollution_index'].mean()
        fig.add_trace(
            go.Scatter(
                x=annual_pollution_all.index,
                y=annual_pollution_all.values,
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=8),
                showlegend=False,
                hovertemplate='<b>Year:</b> %{x}<br><b>Pollution Index:</b> %{y:.1f}<extra></extra>'
            ),
            row=3, col=1
        )
        
        if not pvp_df.empty and 'population' in pvp_df.columns:
            pvp_sorted = pvp_df.sort_values(['county', 'year'])
            pvp_sorted['pop_growth_yoy'] = pvp_sorted.groupby('county')['population'].pct_change() * 100
            growth_data = pvp_sorted[pvp_sorted['pop_growth_yoy'].notna()].copy()
            
            if len(growth_data) > 0:
                for year in sorted(growth_data['year'].unique()):
                    year_data = growth_data[growth_data['year'] == year].nlargest(10, 'pop_growth_yoy')
                    fig.add_trace(
                        go.Bar(
                            x=year_data['county'],
                            y=year_data['pop_growth_yoy'],
                            name=f'{int(year)}',
                            text=[f'{v:.1f}%' for v in year_data['pop_growth_yoy']],
                            textposition='auto',
                            hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
                        ),
                        row=3, col=2
                    )
        
        if not pvp_df.empty:
            national_pop_by_year = pvp_df.groupby('year')['population'].sum().reset_index()
            national_pop_by_year.columns = ['year', 'total_population']
            
            fig.add_trace(
                go.Bar(
                    x=national_pop_by_year['year'].astype(str),
                    y=national_pop_by_year['total_population'],
                    marker=dict(color=['#3498db', '#2ecc71', '#e74c3c']),
                    text=[f'{v/1e6:.2f}M' for v in national_pop_by_year['total_population']],
                    textposition='auto',
                    showlegend=False,
                    hovertemplate='<b>Year:</b> %{x}<br><b>Population:</b> %{y:,.0f}<extra></extra>'
                ),
                row=4, col=1
            )
        
        county_pop = integrated_df.groupby('county')['population'].first().sort_values(ascending=False).head(12)
        fig.add_trace(
            go.Bar(
                x=county_pop.index,
                y=county_pop.values,
                marker=dict(color='green'),
                text=[f'{v/1000:.0f}K' for v in county_pop.values],
                textposition='auto',
                showlegend=False
            ),
            row=4, col=2
        )
        
        # Use pre-calculated pollution-water correlation from analyzer
        if 'pollution_water' in correlations and not correlations['pollution_water'].empty:
            pw_corr = correlations['pollution_water']
            pw_corr = pw_corr.dropna(how='all', axis=0).dropna(how='all', axis=1)
            if not pw_corr.empty:
                fig.add_trace(
                    go.Heatmap(
                        z=pw_corr.values,
                        x=pw_corr.columns,
                        y=pw_corr.index,
                        colorscale='RdBu',
                        zmid=0,
                        text=np.round(pw_corr.values, 2),
                        texttemplate='%{text}',
                        showscale=False
                    ),
                    row=5, col=1
                )
        
        for county in integrated_df['county'].unique()[:12]:
            county_data = integrated_df[integrated_df['county'] == county]
            fig.add_trace(
                go.Scatter(
                    x=county_data['pollution_index'],
                    y=county_data['avg_quality_score'],
                    mode='markers',
                    name=county,
                    text=county_data['year'],
                    hovertemplate='<b>%{fullData.name}</b><br>Pollution: %{x:.1f}<br>Water Quality: %{y:.1f}<br>Year: %{text}<extra></extra>'
                ),
                row=5, col=2
            )
        
        df_2022 = integrated_df[integrated_df['year'] == 2022].copy()
        if len(df_2022) > 0:
            fig.add_trace(
                go.Scatter(
                    x=df_2022['population'],
                    y=df_2022['avg_quality_score'],
                    mode='markers+text',
                    text=df_2022['county'],
                    textposition='top center',
                    marker=dict(size=12, color='purple'),
                    showlegend=False
                ),
                row=6, col=1
            )
        
        if 'overall' in correlations and not correlations['overall'].empty:
            corr_matrix = correlations['overall']
            corr_pairs = []
            corr_values = []
            
            if 'pollution_index' in corr_matrix.index and 'avg_quality_score' in corr_matrix.columns:
                corr_pairs.append('Pollution vs Water Quality')
                corr_values.append(corr_matrix.loc['pollution_index', 'avg_quality_score'])
            
            if 'pollution_index' in corr_matrix.index and 'total_national_population' in corr_matrix.columns:
                corr_pairs.append('Pollution vs National Population')
                corr_values.append(corr_matrix.loc['pollution_index', 'total_national_population'])
            
            if 'population' in corr_matrix.index and 'avg_quality_score' in corr_matrix.columns:
                corr_pairs.append('Population vs Water Quality')
                corr_values.append(corr_matrix.loc['population', 'avg_quality_score'])
            
            if corr_pairs:
                colors = ['red' if v < 0 else 'green' for v in corr_values]
                fig.add_trace(
                    go.Bar(
                        x=corr_values,
                        y=corr_pairs,
                        orientation='h',
                        marker=dict(color=colors),
                        text=[f'{v:.3f}' for v in corr_values],
                        textposition='auto',
                        showlegend=False
                    ),
                    row=6, col=2
                )
        
        # Use pre-calculated overall correlation matrix from analyzer
        if 'overall' in correlations and not correlations['overall'].empty:
            corr_matrix = correlations['overall']
            corr_matrix = corr_matrix.dropna(how='all', axis=0).dropna(how='all', axis=1)
            if not corr_matrix.empty:
                fig.add_trace(
                    go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.index,
                        colorscale='RdBu',
                        zmid=0,
                        text=np.round(corr_matrix.values, 2),
                        texttemplate='%{text}',
                        showscale=False
                    ),
                    row=7, col=1
                )
        
        # Widget 14: Estimated County Emissions (2022)
        if len(df_2022) > 0 and 'estimated_county_emissions' in df_2022.columns:
            df_2022_clean = df_2022.dropna(subset=['estimated_county_emissions'])
            
            if len(df_2022_clean) > 0:
                county_data = df_2022_clean.nlargest(min(12, len(df_2022_clean)), 'estimated_county_emissions')
                
                fig.add_trace(
                    go.Bar(
                        x=county_data['county'],
                        y=county_data['estimated_county_emissions'],
                        marker=dict(color='orange'),
                        text=[f'{v/1000:.1f}K' for v in county_data['estimated_county_emissions']],
                        textposition='auto',
                        showlegend=False,
                        hovertemplate='<b>%{x}</b><br>Estimated emissions: %{y:,.0f} tonnes<br>(Based on population proportion)<extra></extra>'
                    ),
                    row=7, col=2
                )
        else:
            # Add placeholder when data not available
            fig.add_trace(
                go.Bar(
                    x=[],
                    y=[],
                    showlegend=False
                ),
                row=7, col=2
            )
            fig.add_annotation(
                text="Data not available<br>(requires estimated_county_emissions)",
                xref="x14", yref="y14",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        
        if not pvp_df.empty and 'population' in pvp_df.columns and 'total_emissions' in pvp_df.columns:
            national_data = pvp_df.groupby('year').agg({
                'total_national_population': 'first',
                'total_emissions': 'first',
                'pollution_index': 'first'
            }).reset_index()
            
            fig.add_trace(
                go.Scatter(
                    x=national_data['total_national_population'],
                    y=national_data['total_emissions'],
                    mode='markers+lines+text',
                    text=national_data['year'].astype(int).astype(str),
                    textposition='top center',
                    marker=dict(size=15, color=['#3498db', '#2ecc71', '#e74c3c']),
                    line=dict(color='gray', width=2, dash='dash'),
                    showlegend=False,
                    hovertemplate='<b>Year:</b> %{text}<br><b>Population:</b> %{x:,.0f}<br><b>Emissions:</b> %{y:,.0f} tonnes<extra></extra>'
                ),
                row=8, col=1
            )
        
        # Widget 16: County Data Comparison Table
        if len(df_2022) > 0 and 'estimated_county_emissions' in df_2022.columns:
            comparison_df = df_2022[['county', 'estimated_county_emissions', 'avg_quality_score', 'population']].copy()
            comparison_df = comparison_df.dropna(subset=['estimated_county_emissions'])
            comparison_df = comparison_df.sort_values('estimated_county_emissions', ascending=False).head(10)
            
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['<b>County</b>', '<b>Est. Emissions (tonnes)</b>', '<b>Water Quality</b>', '<b>Population</b>'],
                        fill_color='paleturquoise',
                        align='left'
                    ),
                    cells=dict(
                        values=[
                            comparison_df['county'],
                            [f"{v:,.0f}" for v in comparison_df['estimated_county_emissions']],
                            [f"{v:.2f}" for v in comparison_df['avg_quality_score']],
                            [f"{v/1000:.0f}K" for v in comparison_df['population']]
                        ],
                        fill_color='lavender',
                        align='left'
                    )
                ),
                row=8, col=2
            )
        else:
            # Add placeholder table when data not available
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['<b>County</b>', '<b>Est. Emissions</b>', '<b>Water Quality</b>', '<b>Population</b>'],
                        fill_color='paleturquoise',
                        align='left'
                    ),
                    cells=dict(
                        values=[
                            ['Data not available'],
                            ['N/A'],
                            ['N/A'],
                            ['N/A']
                        ],
                        fill_color='lavender',
                        align='left'
                    )
                ),
                row=8, col=2
            )
        
        stats_data = [
            ['Counties Analyzed', str(integrated_df['county'].nunique())],
            ['Years Covered', f"{integrated_df['year'].min()}-{integrated_df['year'].max()}"],
            ['Avg Pollution Index', f"{integrated_df['pollution_index'].mean():.1f}"],
            ['Avg Water Quality', f"{integrated_df['avg_quality_score'].mean():.2f}"],
            ['Total Population (2022)', f"{integrated_df[integrated_df['year']==2022]['population'].sum()/1e6:.2f}M"],
            ['Data Points', str(len(integrated_df))],
            ['Pollution Range', f"{integrated_df['pollution_index'].min():.1f} - {integrated_df['pollution_index'].max():.1f}"],
            ['Water Quality Range', f"{integrated_df['avg_quality_score'].min():.2f} - {integrated_df['avg_quality_score'].max():.2f}"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Metric</b>', '<b>Value</b>'],
                    fill_color='lightblue',
                    align='left',
                    font=dict(size=12, color='black')
                ),
                cells=dict(
                    values=[[row[0] for row in stats_data], [row[1] for row in stats_data]],
                    fill_color='white',
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=9, col=1
        )
        
        quality_data = [
            ['Total Records', str(len(integrated_df))],
            ['Missing Pollution Data', str(integrated_df['pollution_index'].isna().sum())],
            ['Missing Water Quality Data', str(integrated_df['avg_quality_score'].isna().sum())],
            ['Missing Population Data', str(integrated_df['population'].isna().sum())],
            ['Complete Records', str(integrated_df.dropna().shape[0])],
            ['Data Completeness', f"{(integrated_df.dropna().shape[0]/len(integrated_df)*100):.1f}%"],
            ['Counties with Full Data', str(integrated_df.groupby('county', group_keys=False).apply(lambda x: x.dropna().shape[0] == len(x), include_groups=False).sum())],
            ['Years with Full Data', str(integrated_df.groupby('year', group_keys=False).apply(lambda x: x.dropna().shape[0] == len(x), include_groups=False).sum())]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(
                    values=['<b>Data Quality Metric</b>', '<b>Value</b>'],
                    fill_color='lightyellow',
                    align='left',
                    font=dict(size=12, color='black')
                ),
                cells=dict(
                    values=[[row[0] for row in quality_data], [row[1] for row in quality_data]],
                    fill_color='white',
                    align='left',
                    font=dict(size=11)
                )
            ),
            row=9, col=2
        )
        
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_yaxes(title_text="Water Quality", row=1, col=1)
        fig.update_xaxes(title_text="Avg Quality Score", row=1, col=2)
        
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Water Quality", row=2, col=1)
        fig.update_xaxes(title_text="County", row=2, col=2)
        fig.update_yaxes(title_text="Water Quality", row=2, col=2)
        
        fig.update_xaxes(title_text="Year", row=3, col=1)
        fig.update_yaxes(title_text="Pollution Index", row=3, col=1)
        fig.update_xaxes(title_text="County", row=3, col=2)
        fig.update_yaxes(title_text="Growth (%)", row=3, col=2)
        
        fig.update_xaxes(title_text="Census Year", row=4, col=1)
        fig.update_yaxes(title_text="Total Population", row=4, col=1)
        fig.update_xaxes(title_text="County", row=4, col=2)
        fig.update_yaxes(title_text="Population", row=4, col=2)
        
        fig.update_xaxes(title_text="Estimated County Emissions (tonnes)", row=5, col=2)
        fig.update_yaxes(title_text="Water Quality Score", row=5, col=2)
        
        fig.update_xaxes(title_text="Population", row=6, col=1)
        fig.update_yaxes(title_text="Water Quality", row=6, col=1)
        fig.update_xaxes(title_text="Correlation Value", row=6, col=2)
        
        fig.update_xaxes(title_text="County", row=7, col=2)
        fig.update_yaxes(title_text="Estimated Emissions (tonnes)", row=7, col=2)
        
        fig.update_xaxes(title_text="National Population", row=8, col=1)
        fig.update_yaxes(title_text="Total Emissions (tonnes)", row=8, col=1)
        
        fig.update_layout(
            height=3200,
            title_text="<b>Ireland Environmental Analysis - Dashboard</b><br>" +
                      "<sub>Organized by Theme: Water Quality, Pollution, Population & Relationships (2009-2024)</sub>",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="bottom",
                y=0.35,
                xanchor="left",
                x=1.01,
                font=dict(size=9),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="black",
                borderwidth=1
            ),
            hovermode='closest',
            font=dict(size=10)
        )
        
        # Generate insights section
        insights_html = self._create_analysis_insights_section(pvp_analysis, pvw_analysis)
        
        # Load template
        template_path = Path(self.template_path)
        if not template_path.exists():
            self.logger.warning(f"Template not found at {template_path}, using fallback")
            template_content = self._get_fallback_template()
        else:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        
        # Generate Plotly chart HTML (div only, no full page)
        plotly_div = fig.to_html(include_plotlyjs='cdn', div_id='plotly-chart', full_html=False)
        
        # Inject content into template
        html_content = template_content.replace('{{INSIGHTS_SECTION}}', insights_html)
        html_content = html_content.replace('{{PLOTLY_CHART}}', plotly_div)
        
        # Write final HTML
        output_path = f'{self.output_dir}/comprehensive_dashboard.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        fig.add_annotation(
            text="Interactive Features: Hover for data values | Toggle series visibility via legend | Pan and zoom enabled | 18 analytical components organized",
            xref="paper", yref="paper",
            x=0.5, y=-0.01,
            showarrow=False,
            font=dict(size=10, color="#2c3e50"),
            xanchor='center',
            align='center',
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#34495e",
            borderwidth=1,
            borderpad=5
        )
        
        self.logger.info(f"Comprehensive dashboard created with 18 widgets: {output_path}")
        
        print(f"\n{'='*60}")
        print("DASHBOARD CREATED")
        print(f"{'='*60}")
        print(f"Location: {output_path}")
        print(f"Widgets: 18 total (organized by theme)")
        print(f"  Row 1: Water Quality Overview")
        print(f"  Row 2: Water Quality Details")
        print(f"  Row 3: Pollution & Population Growth")
        print(f"  Row 4: Population Analysis")
        print(f"  Row 5: Water vs Pollution Comparator")
        print(f"  Row 6: Water vs Population")
        print(f"  Row 7: Pollution Analysis")
        print(f"  Row 8: Population-Pollution Correlation")
        print(f"  Row 9: Statistics & Data Quality")
        print(f"Counties: {integrated_df['county'].nunique()}")
        print(f"Water Years: {integrated_df['year'].min()}-{integrated_df['year'].max()}")
        print(f"Pollution Years: 2009-2023 (all years shown)")
        print(f"Census Years: 2011, 2016, 2022")
        print(f"Data Points: {len(integrated_df)}")
        print(f"{'='*60}\n")

    
    def _create_analysis_insights_section(self, pvp_analysis: Dict[str, Any], pvw_analysis: Dict[str, Any]) -> str:
        """Create HTML section documenting multi-dataset analytical findings"""
        
        insights_html = """
        <div class="insights-section">
            <h2>Multi-Dataset Integration Results</h2>
            <p>Statistical analysis across census periods (2011, 2016, 2022) and water quality monitoring (2021-2024)</p>
        """

        insights_html = self._pollution_to_population_graphs(insights_html, pvp_analysis)
        insights_html = self._pollution_to_water_graphs(insights_html, pvw_analysis)

        # Dataset 3 note
        insights_html += """
        <div class="insight-card">
            <h3>Analysis 3: Integrated Water Quality-Demographics Dataset</h3>
            <div class="insight-card-content">
                <p><strong>Integration Approach:</strong> Primary analytical dataset combining water quality monitoring with demographic census data (visualized in components 1-15 above).</p>
                <p><strong>Temporal Scope:</strong> Water quality observation period (2021-2024) with 2022 census baseline propagated to non-census years.</p>
                <p><strong>Analytical Purpose:</strong> Facilitates county-level assessment of water quality temporal patterns within demographic context.</p>
            </div>
        </div>
        """
        
        insights_html += """
        </div>
        """
        
        return insights_html

    def _pollution_to_water_graphs(self, insights_html, pvw_analysis) -> Any:
        if pvw_analysis:
            insights_html += """
            <div class="insight-card">
                <h3>Analysis 2: Emissions-Water Quality Relationship</h3>
                <div class="insight-card-content">
            """

            if 'years_covered' in pvw_analysis:
                years = pvw_analysis['years_covered']
                insights_html += f"<p><strong>Temporal Coverage:</strong> {', '.join(map(str, years))}</p>"

            if 'pollution_water_correlation' in pvw_analysis:
                corr = pvw_analysis['pollution_water_correlation']
                sig_text = "statistically significant (p < 0.05)" if corr.get('significant',
                                                                              False) else "not statistically significant (p ≥ 0.05)"
                interp = corr.get('interpretation', 'unknown')
                insights_html += f"""
                <p><strong>Emissions-Water Quality Correlation Coefficient:</strong> r = {corr.get('coefficient', 0):.3f} ({sig_text})</p>
                <p style="margin-left: 20px; color: #555;">Relationship Strength: {interp.capitalize()}</p>
                """

            if 'pollution_trend' in pvw_analysis:
                trend = pvw_analysis['pollution_trend']
                insights_html += f"""
                <p><strong>Emission Temporal Trend:</strong> {trend.get('direction', 'unknown').capitalize()} trajectory (R² = {trend.get('r_squared', 0):.3f})</p>
                """

            if 'water_quality_trend' in pvw_analysis:
                trend = pvw_analysis['water_quality_trend']
                insights_html += f"""
                <p><strong>Water Quality Temporal Trend:</strong> {trend.get('direction', 'unknown').capitalize()} trajectory (R² = {trend.get('r_squared', 0):.3f})</p>
                """

            if 'best_water_county' in pvw_analysis and 'worst_water_county' in pvw_analysis:
                insights_html += f"""
                <p><strong>Water Quality Performance Rankings:</strong></p>
                <ul style="margin: 5px 0 0 20px;">
                    <li>Highest Quality: {pvw_analysis['best_water_county']}</li>
                    <li>Lowest Quality: {pvw_analysis['worst_water_county']}</li>
                </ul>
                """

            insights_html += """
                </div>
            </div>
            """
        return insights_html

    def _pollution_to_population_graphs(self, insights_html, pvp_analysis) -> Any:
        if pvp_analysis:
            insights_html += """
            <div class="insight-card">
                <h3>Analysis 1: Emissions-Demographics Relationship (Census Periods)</h3>
                <div class="insight-card-content">
            """

            if 'census_years' in pvp_analysis:
                census_years = pvp_analysis['census_years']
                insights_html += f"<p><strong>Census Observation Points:</strong> {', '.join(map(str, census_years))}</p>"

            if 'overall_changes' in pvp_analysis:
                changes = pvp_analysis['overall_changes']
                insights_html += f"""
                <p><strong>National-Level Temporal Changes ({changes.get('years_span', 'N/A')}):</strong></p>
                <ul style="margin: 5px 0 15px 20px;">
                    <li>Emission Trajectory: <span style="color: {'#e74c3c' if changes.get('pollution_change_pct', 0) > 0 else '#27ae60'}; font-weight: bold;">{changes.get('pollution_change_pct', 0):.1f}%</span></li>
                    <li>Population Growth: <span style="color: {'#e67e22' if changes.get('population_change_pct', 0) > 0 else '#3498db'}; font-weight: bold;">{changes.get('population_change_pct', 0):.1f}%</span></li>
                </ul>
                """

            if 'population_emissions_correlation' in pvp_analysis:
                corr = pvp_analysis['population_emissions_correlation']
                sig_text = "statistically significant (p < 0.05)" if corr.get('significant',
                                                                              False) else "not statistically significant (p ≥ 0.05)"
                insights_html += f"""
                <p><strong>Population-Emissions Correlation Coefficient:</strong> r = {corr.get('coefficient', 0):.3f} ({sig_text})</p>
                """

            if 'top_growing_counties' in pvp_analysis:
                top_counties = pvp_analysis['top_growing_counties']
                insights_html += "<p><strong>Highest Population Growth Rates (Top 5 Counties):</strong></p><ul style='margin: 5px 0 0 20px;'>"
                for county in top_counties[:5]:
                    insights_html += f"<li>{county['county']}: +{county['population_change_pct']:.1f}% intercensal change</li>"
                insights_html += "</ul>"

            insights_html += """
                </div>
            </div>
            """
        return insights_html

    def _get_fallback_template(self) -> str:
        """Fallback template if template file is not found"""
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ireland Environmental Analysis Dashboard</title>
</head>
<body>
    <h1>Ireland Environmental Analysis Dashboard</h1>
    {{INSIGHTS_SECTION}}
    {{PLOTLY_CHART}}
</body>
</html>"""
