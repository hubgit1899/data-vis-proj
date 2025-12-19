# Uncovering the Shadows on Our Roads: A Data Science Journey

> **Authors**: The DataViz Team  
> **Date**: December 2025

---

## 1. The Spark: A Simple Question

It started with a debate in our group chat. We were looking at traffic accident statistics and wondered: **Does education level actually affect how safe a community's roads are?**

It sounds a bit judgmental at first, right? "Do smarter people drive better?" But that's not what we meant. We wanted to know if communities with lower access to higher education—often tied to economic challenges—were facing a hidden crisis on their roads. 

So, we decided to dig in. We didn't just want numbers; we wanted the story behind them.

## 2. The Data Hunt

We needed *a lot* of data. We turned to the **NHTSA FARS (Fatality Analysis Reporting System)**, a massive government database recording every fatal crash in the US. We grabbed everything from **2010 to 2023**. That’s 14 years of tragedy, millions of data points.

To compare this with education, we pulled **US Census data**, specifically looking at the percentage of adults without a high school diploma vs. those with bachelor's degrees in every single county.

Merging these was... a nightmare. FIPS codes, changing column names (seriously, why change "WEATHER" to "WEATHER1"?), and messy formats. But after writing some extensive Python scripts (which you can see in our `code/` folder), we built a **Master Dataset** covering over 3,000 counties for over a decade.

## 3. What We Found: The "Introduction" to EDA

We started with **Exploratory Data Analysis (EDA)** just to see what the data looked like.

### The Big Picture
First, we looked at the trends over time. Are our roads getting safer?

![Temporal Trends](../output/03_temporal_trends.png)
*Fig 1: Total traffic fatalities vs accidents over the last decade.*

As you can see, while cars are getting safer, the number of fatalities hasn't just dropped to zero. In fact, in recent years, we've seen worrying spikes.

### The "Education Paradox"
Here’s where it got weird. When we first plotted the raw number of accidents against education levels, it looked like **highly educated counties had MORE accidents.**

We were confused. Then it hit us: **Population.**

Places with high education levels are usually cities (New York, San Francisco, Boston). Cities have millions of people. More people = More cars = More accidents.
Rural areas often have lower education rates but way fewer people.

So, we had to **normalize** the data. We stopped calculating "Total Accidents" and started calculating **"Fatalities per 100,000 People"**.

![Education vs Fatality Rate](../output/02_edu_vs_fatality.png)
*Fig 2: Once we corrected for population, the truth came out.*

The trend line flip-flopped. Communities with **lower education levels** (higher % without High School) actually have **higher fatality rates per capita**. The connection was real. But why?

## 4. Digging Deeper: The "Why" (Explanatory Analysis)

We couldn't just say "it's education" and walk away. That’s lazy science. We needed to find the **Risk Factors**. We ran a Principal Component Analysis (PCA) and detailed clustering algorithms to find hidden patterns.

### The Culprits: Alcohol and Darkness

We investigated specific conditions:
1.  **Drunk Driving**: Are these crashes alcohol-fueled?
2.  **Nighttime/Darkness**: Are roads poorly lit?
3.  **Weather**: Is it just rain?

![Alcohol by Education](../output/04_alcohol_by_edu.png)
*Fig 3: Percentage of impairment-related crashes by education group.*

The data showed a heartbreaking trend. Counties with lower education metrics often struggled significantly more with **alcohol-impaired driving** and **nighttime accidents**.

### The Urban-Rural Divide
We realized that "Education" was often a proxy for "Rurality". When we split the data by urban vs. rural classifications, the disparity became even starker.

![Fatality by Urbanicity](../output/16_box_urbanicity_fatality.png)
*Fig 4: Rural areas consistently show higher fatality rates.*

### Weathering the Storm
Interestingly, while we hypothesized weather played a huge role, the data showed it was less significant than alcohol.

![Weather vs Fatality](../output/12_scatter_weather_fatality.png)
*Fig 5: Adverse weather has a weaker correlation with fatalities than expected.*

### The Rural Reality
Our clustering analysis revealed distinct "Safety Archetypes".

![Safety Clusters](../output/exda_02_clusters.png)
*Fig 6: Clustering counties based on risk profiles.*

We found a clear group of counties (often rural) that formed a "High Risk" cluster. In these areas, it's not just about "driving skills." It's about:
*   **Infrastructure**: Dark, unlit rural roads are unforgiving up compared to well-lit city streets.
*   **Distance**: Hospitals are further away. A crash that is an injury in a city becomes a fatality in the country.
*   **Behavior**: Higher rates of unbuckled drivers and alcohol use.

## 5. Conclusion

Our journey started with a question about education, but it ended with a conversation about **inequality**.

The data suggests that the "Education Gap" in road safety is actually an **Infrastructure and Resource Gap**. Lower-literacy communities aren't inherently "bad drivers." They are often driving on darker, more dangerous roads, in older cars, with medical help further away.

If we want to fix this, we don't just need more diplomas. We need better roads, better rural emergency services, and continued support for anti-drunk driving campaigns in these specific communities.

Data helps us see the problem. Now it's up to us to drive the solution.

---
*Generated by the DataViz Team using Python, Pandas, and Seaborn.*
