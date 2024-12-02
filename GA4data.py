import streamlit as st
from google.analytics.data_v1beta import (
    BetaAnalyticsDataClient,
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    FilterExpression,
    Filter,
)
import csv
from datetime import date
# final 30-Nov-2024
# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'SERVICE_ACCOUNT_FILE.json'

# Initialize the client
client = BetaAnalyticsDataClient.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Fixed GA4 property ID
PROPERTY_ID = 'GA4 Property ID'

# Function to build combined filter expression
def build_filter_expression(filter_inputs):
  filters = []
  for user_filter in filter_inputs:
    if user_filter["dimension_metric"] and user_filter["condition"] and user_filter["value"]:
      condition_map = {
          # Previous filters
          "equals": "EXACT",
          "contains": "CONTAINS",
          "starts_with": "BEGINS_WITH",
          "ends_with": "ENDS_WITH",
          "greater_than": "GREATER_THAN",
          "less_than": "LESS_THAN",
          "in_list": "IN_LIST",
          # New filters
          "exact match": "EXACT",
          "does not contain": "CONTAINS",
          "does not begin with": "BEGINS_WITH",
          "does not end with": "ENDS_WITH",
          "regular expressions": "REGEXP",
      }
      negate_conditions = [
          "does not contain",
          "does not begin with",
          "does not end with",
      ]

      # Handle `in_list` filter specifically
      if user_filter["condition"] == "in_list":
          filter_expr = FilterExpression(
              filter=Filter(
                  field_name=user_filter["dimension_metric"],
                  in_list_filter=Filter.InListFilter(
                      values=user_filter["value"].split(",")
                  ),
              )
          )
      else:
          filter_expr = FilterExpression(
              filter=Filter(
                  field_name=user_filter["dimension_metric"],
                  string_filter=Filter.StringFilter(
                      value=user_filter["value"],
                      match_type=condition_map[user_filter["condition"]],
                      case_sensitive=False,
                  ),
              )
          )

      # Wrap in a `not_expression` if negation is required
      if user_filter["condition"] in negate_conditions:
          filter_expr = FilterExpression(not_expression=filter_expr)

      filters.append(filter_expr)

  # Combine all filters using `and_group` only if there's more than one filter
  if len(filters) > 1:
    return FilterExpression(
        and_group=FilterExpression.AndGroup(expressions=filters)
    )
  elif filters:  # Handle case with a single filter
    return filters[0]  # Return the single filter object
  return None
# Function to fetch GA4 data
def fetch_ga4_data(dimensions, metrics, start_date, end_date, filter_expression, output_file):
    dimensions_obj = [Dimension(name=dim.strip()) for dim in dimensions]
    metrics_obj = [Metric(name=metric.strip()) for metric in metrics]
    offset = 0
    LIMIT = 50000  # Maximum rows per request

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        is_header_written = False

        while True:
            request = RunReportRequest(
                property=f"properties/{PROPERTY_ID}",
                dimensions=dimensions_obj,
                metrics=metrics_obj,
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=LIMIT,
                offset=offset,
                dimension_filter=filter_expression,
            )

            response = client.run_report(request)

            if not is_header_written:
                dimension_headers = [header.name for header in response.dimension_headers]
                metric_headers = [header.name for header in response.metric_headers]
                header = dimension_headers + metric_headers
                writer.writerow(header)
                is_header_written = True

            for row in response.rows:
                dimension_values = [dimension_value.value for dimension_value in row.dimension_values]
                metric_values = [metric_value.value for metric_value in row.metric_values]
                writer.writerow(dimension_values + metric_values)

            if len(response.rows) < LIMIT:
                break
            offset += LIMIT

# Streamlit Interface
st.title("GA4 Data Export Tool with Full Filter Options")
st.header(date.today())
st.write("Specify dimensions, metrics, date range, and filters to fetch GA4 data.")

# User Inputs
dimensions_input = st.text_input("Dimensions", placeholder="Enter dimensions separated by commas (e.g., city, browser)")
metrics_input = st.text_input("Metrics", placeholder="Enter metrics separated by commas (e.g., activeUsers, sessions)")
start_date = st.date_input("Start Date", value=date(2024, 11, 1))
end_date = st.date_input("End Date", value=date.today())

# Filters
st.write("### Add Filters (Optional)")
filters_input = []
num_filters = st.number_input("Number of filters", min_value=0, max_value=10, value=0, step=1)

for i in range(num_filters):
    st.write(f"Filter {i + 1}")
    dimension_metric = st.text_input(f"Dimension/Metric Name for Filter {i + 1}", key=f"dimension_metric_{i}")
    condition = st.selectbox(
        f"Condition for Filter {i + 1}",
        [
            # Previous filters
            "equals",
            "contains",
            "starts_with",
            "ends_with",
            "greater_than",
            "less_than",
            "in_list",
            # New filters
            "exact match",
            "does not contain",
            "does not begin with",
            "does not end with",
            "regular expressions",
        ],
        key=f"condition_{i}",
    )
    value = st.text_input(f"Value for Filter {i + 1}", key=f"value_{i}")
    filters_input.append({"dimension_metric": dimension_metric, "condition": condition, "value": value})

# File Output Name with Start and End Dates
output_file = f"ga4_data_export_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.csv"

# Run the Export Process
if st.button("Fetch Data"):
    if not dimensions_input or not metrics_input:
        st.error("Please fill in all fields!")
    else:
        try:
            st.info("Fetching data. This might take a few moments...")
            filter_expression = build_filter_expression(filters_input)
            fetch_ga4_data(
                dimensions=dimensions_input.split(","),
                metrics=metrics_input.split(","),
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                filter_expression=filter_expression,
                output_file=output_file,
            )
            st.success(f"Data export complete! File saved as {output_file}")
            with open(output_file, "rb") as file:
                st.download_button(
                    label="Download CSV File",
                    data=file,
                    file_name=output_file,
                    mime="text/csv",
                )
        except Exception as e:
            st.error(f"An error occurred: {e}")
