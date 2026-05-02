# Login

Users to get access to application by being added to the Okta user group . SSO Login: All Bain users (added to the above group) have SSO login enabled. Users have access to only limited case(s) which will be controlled by the admin users. Initially this is controlled by running SQL queries to add/modify user access with Admin page to be added post MVP. On Login user will land on Home page with a list of cases accessible to the user or can create a new case. Below is a tentative landing page design

The login landing page displays a personalized welcome message and a navigation panel on the left, allowing users to create a new company or access various sections such as 'All companies', 'My companies', and 'Bookmarked companies'. The main area shows a grid of company cards with details like industry, revenue, and headcount, along with options to sort by these criteria. Each card includes the company's name, financial metrics, and last update date. This screen helps users quickly access and manage their business cases, providing an overview of available companies and facilitating navigation through the platform.

# Site Navigation

## Navigation Bar

The navigation bar displayed is part of the site navigation workflow, showing various sections and options available to the user after completing the tool setup process. Key sections include 'Explore & adjust input data' with options like 'Employee', 'GL', and 'Aggregated View', and 'Assessments' which further divides into 'Benchmarking', 'Shared Services', 'Automation', and 'Integrated View', each with sub-options such as 'Data upload', 'Explore benchmark', 'Assumptions', and 'Output'. At the bottom, the 'Tool setup' menu provides access to 'Company profile', 'Assessment & functional taxonomy', and 'Upload client data'. This navigation bar helps users efficiently access different parts of the platform based on their selected assessments.

Navigation bar is case specific. It will display only the options depending on the assessments selected by the user.

At the bottom of the navigation bar is the “Tool Setup” menu. Users can use these options to go to the setup pages at any time during the analysis.

When a user start creating a case for the first time, they will not see any navigation bar. The navigation is made visible only after the user has completed the tool setup process.

# Admin Page

1. To be picked later

# Company Overview

## Purpose

This is the Landing page for the user when starting a new case. This will collect high level info regarding the company

The 'Company Overview > Purpose' screen is the initial landing page for users starting a new business case. It features a 'Company profile' form where users can input high-level company information, including fields for Company Name, Industry, Company Revenue, Total Headcount, Currency, and Exchange Rate. The top navigation bar outlines the workflow steps: Create company profile, Select assessment and functional taxonomy, Upload client data, and Upload benchmarks. A 'Next stage' button is present to proceed, and an 'Abandon company' option allows users to exit the process. This screen facilitates the setup of a new company profile by collecting essential business context data.

## Validations

- All fields are mandatory
- No of employees cannot be negative and should only input numbers
- Exchange rate should be >0
- Company revenue should be >0

## Click actions

### Abandon company

Any details entered are removed and user is redirected to Home page. No new case is created

### Next Stage

Check all validations are met. A new case is created in the database. User is directed to the assessment selection page

## Form actions

Exchange rate will be populated from a standard table in the DB. The exchange rate data will be updated on a quarterly basis by the COE. However, the user has rights to update the exchange rate manually.

# Assessment Selection and setup

## Purpose

This page captures the assessments that the user wants to run

The Assessment Selection and Setup screen allows users to choose the assessments they wish to conduct, such as Top-down Benchmarking, Shared Services Opportunity Assessment, and Automation/AI Opportunity Assessment. Users can select business functions like Finance, HR, IT, Legal, Facility Management, and Operations, and configure options for Renaming, Benchmarking, Shared Services, and Automation levels. The interface includes checkboxes for selecting assessments, dropdown menus for setting levels, and an 'Add business function' button to include additional functions. This screen facilitates the customization and setup of assessments tailored to specific business needs.

## Page actions

### Assessment selection

Users can select one or more assessments. Based on the assessment selected, business functions displayed would vary.

Ex: If a user selects only Benchmarking and “Operations” function is not present for it , then it will not be shown in the list

### Key note

### Functions and granularity level selection

- Relevant functions to be displayed based on assessments selected
- For all assessments “L2” to be selected by default
- In case a selected level is not applicable for an assessment, when a user selects that level, they will get an error immediately below the dropdown saying “No benchmarks available”
- All functions to be assorted as given in figma. Any new custom fields added by user will be added at the bottom of the list.

### Feature /Processes/Activities selection page

- Once the features are selected, user moves to the next page to select L2 and L3 layer. Only the functions selected in previous pages are displayed here.
- Users can click on the “Edit” button to display the list of L2 levels for the Function.
- L2 levels will be displayed as editable text that the user can easily rename them.
- L3 levels will be shown as a slidedown when a L2 level is clicked upon. These will also be editable directly
- Users can add both custom L2 and L3 levels but if they define a L2 level they are responsible to define the lower L3 hierarchy for the same

The Feature/Processes/Activities selection page allows users to review and edit the taxonomy of each business function. It displays a list of functions such as Finance, HR, IT, Legal, Facility Management, Marketing, and Operations, each with an 'Edit' button to modify the L2 and L3 levels. Users can rename these levels directly and add custom hierarchies. The page includes a 'Reset to default' option for each function, enabling users to revert changes. Navigation options include a 'Back' button and a 'Next stage' button to proceed in the workflow.

The image shows the 'Edit Finance' page within the Feature/Processes/Activities selection workflow. Users can rename, add, or delete L2 processes or L3 activities related to Finance. The page displays a list of processes such as 'Financial Planning & Analysis' and 'Control/Internal Audit,' each with options to edit or delete. Users can expand or collapse sections to view or modify underlying activities. An 'Add activity' button allows users to introduce new activities, while 'Cancel' and 'Save & Update' buttons enable users to discard or save changes, respectively, facilitating customization of financial processes.

### Template column selection page

- Users will select the template they want to input data. The options are dependent on the assessment selected. HRIS and GL files are present for all assessments but a third option appears for Outsourced files if a user selects SSOI as one of the assessments.
- The user can then select the relevant columns for which they plan to run the assessments

The Template Column Selection page allows users to choose templates for data input based on the selected assessment. The screen displays options for HR Baseline and GL Baseline templates, with checkboxes to select them. Each template has a preview section listing field names such as 'Unique ID' and 'Employee type' for HR Baseline, and 'Functional Allocation' for GL Baseline. Users can add fields using the 'Add field' button. This page facilitates the customization of data templates, enabling users to tailor the data input process to their specific assessment needs.

### Upload templates

- Users will upload the Baseline data from this page. The columns included in the files are dynamic as they are dependent on the selections made by the user in previous step.

The 'Upload templates' screen allows users to upload baseline data files for HR and GL categories. It features sections for each category, each with a 'Download template' button to obtain a CSV template and a drag-and-drop area for file uploads. Users are instructed to upload CSV files no larger than 20MB, with a link to an FAQ for additional guidance. This screen facilitates the data upload process by providing necessary templates and a straightforward interface for file submission, ensuring users can efficiently prepare and upload their data for analysis.

### Upload validations

Any files uploaded by the user go through multiple validations before the data is inserted in the database.

### Columns check

The columns in the uploaded file are checked against the list of columns selected in previous steps. In case of any missing columns or additional columns, an error is displayed on the screen which lists the missing/additional columns. Users need to update their files and reupload the files OR they can choose to add/remove columns from the previous page to match the column list of their file

### File specific validations

Headcount/Outsource:

1. Employee ID should be unique: Employee ID is not a mandatory field but if included the IDs should be unique
2. FTE allocation should be <= 100% : Capacity allocation of any employee cannot be more than 100%

GL:

1. In case any validations fail, then the user is prompted regarding errors. They can download the error file which provides a list of error against each row specifying the validation which failed for that particular row. User can then fix the file and upload the file again after removing the error column.

### Preview templates

Once the validations succeed, user is shown a “read-only” preview of the uploaded file so they can cross check that the file has been uploaded successfully and correctly.

# Data upload page

## Purpose

The Data Upload screen allows users to upload the essential input files (such as HR Baseline and GL data) that provide the base client data for all the assessments

## Core Functional Requirements

The data upload page for HR and GL Baseline files allows users to upload CSV files up to 20MB. It features separate sections for HR Baseline and GL Baseline uploads, each with a 'Download template' button to obtain sample files. Users can drag and drop files into designated areas for upload. The page provides guidance on file size limits and links to FAQs for additional support. This screen facilitates the initial step of data integration by enabling users to upload necessary baseline data for further analysis.

### File Upload Functionality

### Upload Types Supported

- HR Baseline File
- GL baseline file
  Supported Formats:xlsx

### File Template Download

Button to download sample/template files for:

- HR Baseline
- GL Baseline

### File Validation on Upload

- Check required columns exist (e.g., Employee ID, Function, Labor Cost, % Allocation)
- Check for missing values in mandatory fields
- Check if numeric columns contain valid numbers
- A singe excel file to be downloaded as output with a list of errors found in the template. User will need to fix the issues and then reupload

## Preview

- On successful validation, a preview of the uploaded file to be shown in a table.
- NO editing option to be provided at this stage
- User will have an option to reupload file in case of any issues
- Re-upload button to replace file

## Integration with Backend

### On successful upload

Data is stored in case specific tables with no interaction with any other case data

# Explore and adjust Baseline

# Benchmarking

## Tool Overview

Benchmarking assessment tool is used to run ben

## Screens

The Benchmarking assessment tool section will have three pages:

- Benchmark Upload
- Explore Benchmarks
- Output

## Benchmark Upload

This page is required to upload the benchmarking data to be used for the assessment.

The Benchmark Upload screen allows users to upload benchmarking data necessary for assessments. It features a 'Download Template' button for obtaining a preformatted Excel file, which users can populate with their data. The screen includes a drag-and-drop area for uploading CSV files, with a size limit of 20MB. Instructions and a link to an FAQ are provided to assist users. This step is crucial for integrating user-specific data into the benchmarking process, enabling subsequent analysis and comparison within the platform.

### Download Template

On clicking the “Download Template” button, an excel file is downloaded in the format shown below.

1. The Template is prefilled with the taxonomy levels selected by the user on the Assessment & Taxonomy selection page.
2. Any functions/processes/activities that have been modified or newly added by the user will be highlighted using a different font color
3. To define the benchmark values for the same taxonomy level for different sets, users need to duplicate the rows
4. For each level , the first row will be considered as the primary/default peer set for that combination. The default peer sets can be changed later from the “Explore Benchmarks” page

Currently the tool offers the following 6 KPIs for comparison:

### Overall cost (needs GL)

1. Cost of X (for L1 function, L2 process or L3 activities) as a % of revenue
2. Cost of X per employee

### Number of employees (needs HC)

1. # of employees in X as a % of total employees
2. # of employees in X per $1B revenue

### Personnel cost (needs GL or HC; consider comment in sticker in GL columns slide)

1. Personnel cost of X as a % of revenue
2. Personnel cost of X per employee

### Validations

Following validations are performed on the benchmarking data:

### KPI values

Checks for the standard KPIs and if any unknown KPIs are present in the data then the above 6

### Data type mismatch

% values provided for KPIs with % metrics and numbers for numerical metrics

### Mandatory fields

Checks that none of the mandatory fields should be blank Validations are performed on the uploaded benchmarks and error file generated similar to the Baseline error file. User would then need to fix the errors and reupload the data

### Benchmark preview

If the file validation is successful, a preview of the updated data is displayed to the user. This is read-only and no editing can be done in this preview. In case the user wants to update the data , they can use the “X” button on top right corner of the preview screen . Alternatively, user can also navigate to the “Explore Benchmarks” page to edit the data.

### Benchmark Summary preview

Using the toggle on the preview page, user can switch the preview page to a summary view. This view shows the count of benchmarks available for each taxonomy level for each KPI. Any taxonomy elements which are present in the baseline data but there is no benchmark provided for them in the uploaded file are highlighted in different color.

Once the user verifies the uploaded benchmark data, they can click on the “Next” button to look at the final analysis.

The Benchmark Summary preview screen displays a detailed table summarizing the uploaded benchmark data. It includes columns for function, process, sub-process, overall cost, number of employees, and personnel cost, with specific metrics such as 'Cost as % of Revenue' and 'Personnel cost per employee'. Users can review the count of benchmarks available for each taxonomy level and identify any missing benchmarks highlighted in a different color. This screen allows users to verify the uploaded data before proceeding to the final analysis by clicking the 'Next stage' button.

## Explore benchmarks

The 'Explore benchmarks' screen displays an editable table for managing benchmark data within a business case. Key UI components include columns for Function, Process, Sub-process, Metric, Peer Set, and Performance metrics such as Top Quartile and Median. Users can add new benchmarks via the 'Add benchmarks' button, which supports Excel uploads for appending data. The 'Reset to Default' option allows reverting to the last saved state. Each row can be expanded for detailed view, and benchmarks can be deleted using the '-' icon. This interface facilitates detailed analysis and customization of benchmark data specific to the current case.

This page provides an Editable table for the Benchmark data.

This view will also show a data views and a summary view, but the summary view will not be editable.

In the data view, users can edit existing benchmark values , add new benchmarks and delete benchmarks. It should be noted that this is specific to the current case and changes do not have any impact to benchmark data being used for any other case.

“Reset to Default” functionality on the top will reset the page to its last saved status of the data. The “-“ sign can be used to delete a benchmark from the data.

In order to add new data , user can click on the “Add benchmarks” button. This is similar to the upload page in the Tool Setup and the user will need to upload new benchmarks data via an excel upload. It should be noted that the excel should contain only the new data rows as this is an append functionality. The old data will not be overwritten by this file upload. The validations for the file will remain safe. In case of any duplicates, the system will remove them by itself and provide a notification to the user.

In case of any error, a benchmark failed status will be shown and error file can be downloaded.

The 'Add benchmarks' overlay allows users to upload additional benchmark data via a CSV file. Key components include a file upload area where users can drag and drop files, a 'Download template' button for obtaining a CSV template, and a 'Cancel' option to exit the overlay. The interface supports files up to 20MB and provides a link to an FAQ for further guidance. This functionality is designed to append new data to the existing benchmarks without overwriting, ensuring seamless integration of additional metrics into the current business case analysis.

The 'Explore benchmarks' screen displays a notification area confirming the successful upload of 58 benchmarks and indicating that 3 duplicates were skipped. The editable table shows detailed benchmark data with columns for Function, Process, Sub-process, Metric, Peer Set, and Performance metrics. Users can manage benchmarks by adding new entries via the 'Add benchmarks' button or resetting changes with 'Reset to Default'. The interface supports detailed analysis and customization of benchmark data specific to the current case, with real-time feedback on data operations.

## Output

The image displays the 'Analysis results' section of the Benchmarking Output page, focusing on the Detailed View. It presents a table with columns for Function, Process, Sub-process, Metric, Baseline Value, and Gap to Benchmark percentages, including Top Quartile, Median, and Bottom Quartile. The table allows users to compare client values against benchmarks for various financial metrics such as 'Cost as % revenue' across different finance-related processes. Users can toggle between different peer sets and view potential savings. This screen aids in detailed analysis by providing comprehensive KPI data for informed decision-making.

Output page provides the benchmarking comparison between the client values and benchmarks uploaded. It contains two views: Summary and Detail view

### Calculations for Client value

- Cost as % revenue :
- Cost of X taxonomy per employee
- # of employees in taxonomy X as as % of total employees
- # of employees in X per $1B revenue
- Personnel cost of X as a % of revenue
- Personnel cost of X per employee

### Summary view

Summary view shows the analysis data for one KPI and peer set at a time. When the user first lands on the page , the view shows a “default” scenario with the taxonomy selected by the user during Tool Setup at the highest granularity. The default metric and peer set are selected. User can chose to change the granularity for each function individually .

### Detailed View

The Detailed view shows the analysis data for all the KPIs available for each taxonomy level but only for one peer set. User can choose to change the peer set at a row level. This view also shows the calculated client value for each KPI.

“Gap to Benchmark” : it should be noted that both the views do not show the actual benchmarking values but only the % gap of the client’s KPI value to the benchmarking value. The user can chose which quartile they want to compare to (Top/Median/Bottom/Custom value) and the savings potential is calculated corresponding to the selected quartile. The selected quartile is highlighted in a “purple” color.

In the “Gap to benchmark” column, a blank value means that no benchmark is available for that quartile. A “-“ means that the client value is already better than the quartile benchmark.

### Saving a Scenario

User can create new scenarios or save old ones (except Default, which would always show the original values). The Save functionality is an event based Save where the scenario gets saved when a user creates a new scenario, switches to a new scenario or moves to a different tab.

# Shared Services

## Tool Overview

The Shared Services Opportunity Indicator (SSOI) is a strategic analysis tool designed to help organizations evaluate, model, and optimize their shared services footprint across business functions such as Finance and HR etc... It supports data-driven decisions for transitioning operations into centralized shared service centers and enables users to simulate multiple future-state scenarios, estimate cost savings, and understand organizational impact.

## Functional Objectives

The tool enables users to:

- Analyze the current state of functional personnel distribution.
- Define and apply benchmark-driven target models.
- Simulate scenarios for shared services adoption.
- Estimate financial impact and FTE movement.
- Generate comparative outputs to aid executive decision-making.

## Screens

Shared Services tool can be divided into three major sections:

### Overall Assumptions

- SSOI Benchmarks
- Site Selection
- Resource allocation
- Site allocation

### One off cost assumptions

- Transition costs
- Severance costs
- Other one-off costs

### Output

- Savings and FTE evolution
- Annual run-rate savings
- FTE impact overall view
- FTE shifts
- One-time cost overview
- Calendar view
- All data table

## Overall assumptions

The 'SSOI: Assumptions' landing page provides an overview of critical and one-off cost assumptions necessary for Shared Services projections. It features sections for 'Overall assumptions' and 'One-off cost assumptions,' each containing interactive cards such as 'Benchmark,' 'Site selection,' 'Site allocation,' and others. Each card includes a brief description and a navigation arrow, guiding users to detailed input pages. This screen helps users define baseline inputs like labor cost, site strategy, and one-off cost estimates, forming the foundation for Shared Services analysis.

This is the main landing page for the SSOI tool. Inputs in the Benchmarks, Site selection and Site allocation pages are compulsory inputs as they provide critical data for the tool analysis.

### SSOI Benchmarks

Benchmarks page is the first page in the SSOI Assumptions module. It is a compulsory input page which a user needs to interact with.

The SSOI Benchmarks page is part of the Overall Assumptions module, displaying a table for users to input and adjust benchmark data. The table includes columns for 'Function/Process/Sub-Process', 'SSC Full Potential', 'Local', 'Regional', 'Global', and 'Customize Site Allocation'. Users can edit benchmark values, ensuring the sum of Local, Regional, and Global columns equals 100%. The 'Process Improvement' section allows setting a 'Client Starting Point' with a default value of 3, adjustable between 1 and 5. A toggle in the 'Customize Site Allocation' column enables site-specific details. The page includes a 'Reset to Default' option for reverting changes.

The first columns is the “Taxonomy” column which will show the L1/L2/L3 in a tree data structure.

The column will only show the taxonomy levels selected by the user for the SSOI analysis even if benchmark data is available in the database for other levels. Benchmark data will be pre uploaded by COE team from backend. This is a common data for all cases, however case specific changes can be made by users.

The page has two sections - Benchmark data and Process Improvement data.

Benchmark section shows the actual values from the Benchmark file. These values are editable but validation will be done that the sum of Local, Regional and Global columns always should be equal to 100%. If a user has defined a custom taxonomy , then the row is shown as empty and the cells are highlighted with red borders

For the PI section, the “client starting point” is set to 3 by default. This point can be changed by the user with range from 1-5 (1 being the least mature and 5 – most mature)

“Enabled Site Allocation” column is a toggle column which can be used to provide details about a certain site. If a user toggles this ON for any site then the site gets displayed in the Resource allocation page where further details can be provided.

If a user attempts to leave page without resolving any error, following error should be shown:

The image displays an error message on the SSOI Benchmarks page, indicating that the percentages for Local, Regional, and Global columns do not sum to 100%. It prompts the user to adjust the values to meet this requirement. The message includes options to 'See error info' for more details, 'Copy error info' for documentation purposes, and a 'Got it!' button to acknowledge the message. This screen helps users identify and correct input errors to ensure data integrity before proceeding with the analysis.

If they still choose to Save then we show a warning sign on the Assumptions landing page.

On clicking Got It, user does not navigate away, they still need to stay on the page to fix the issue.

“Reset to Default” : This resets the benchmark to its last saved status. Eevery row also has individual “Rest to default” icons, clicking on these icons resets any changes made to that row.

### Site Selection

The 'Site Selection' screen allows users to manage labor costs for different sites within a scenario, such as 'Restructuring, Q3 2025'. It displays a table listing countries, SSC sites, types of SSC, current FTEs, and average fully loaded costs per FTE. Users can propose new labor costs for new FTEs in an editable column. The screen includes options to rename or create new scenarios and add new locations. This interface helps users define and adjust labor costs at various sites, ensuring compliance with benchmarking standards by proposing new sites if necessary.

The 'Site Selection' screen displays a detailed table for managing labor costs across various sites, focusing on the 'Restructuring, Q3 2025' scenario. It includes columns for country, SSC sites, type of SSC, current FTEs, and average fully loaded costs per FTE. Users can propose new labor costs for new FTEs in specific departments such as Finance, HR, IT, Legal, Facility Management, and Operations, with expandable sections for each. The interface allows users to add new locations and toggle between in-house and outsourced options, facilitating comprehensive site-level cost management and compliance with benchmarking standards.

“Site Selection” screen can be used by the users to define the cost of labor at each site. They can define this at a site level or drill down to the lowest granularity level and define the labor cost at that level.

The default view shows the average labor cost for each site calculated from the baseline data. The “Average labor cost” is a read only column and cannot be edited by the user as it is the actual average labor cost from baseline data. However, user can propose a new labor cost for each site in the “Labor cost for new FTEs” column.

Users can also propose creation of new sites to comply with the benchmarking standards. However, this view is connected to the benchmarking view. If there is at least one % >0 in local or regional or global, user must have at least one equivalent site (e.g., one local if at least one process as a >0 in the previous, etc.). An error message would be shown to the user if the above condition is not met.

The 'Site Selection' screen highlights the addition of a new location entry, labeled 'New Location,' within the 'Restructuring, Q3 2025' scenario. This entry is categorized as a 'Local' type of SSC, with editable fields for proposing labor costs for new FTEs. The interface includes a toggle between 'In-house' and 'Outsourced' options, and a button to add more locations. This screen facilitates the expansion of site options and allows users to input proposed labor costs, ensuring alignment with benchmarking standards and enabling detailed site-level cost management.

### Resource allocation

The 'Resource Allocation' screen within the Shared Services section allows users to adjust resource allocations by site. It features a table displaying site codes, types, and baseline versus target allocations across Non-SSC, Local, Regional, and Global categories. Users can increment or decrement values by 0.1 to ensure the total allocations match the FTE count. A warning message indicates overstaffed or understaffed categories, highlighted in red, requiring adjustments. The balance column shows discrepancies that need correction, and an error is displayed if allocations are not balanced. Allocation restrictions prevent moving resources between certain site levels.

This view is an optional view. This is available only if the user selects the toggle in the Benchmarking view. It allows the user to change the resource allocation by site. It can be done only at a site level and at the lowest granularity of the taxonomy.

The values in the screen can be changed in increment/decrement of 0.1 and the total value of the allocations should always match the total FTE count. If the user changes any allocation, a balance is shown in last column/row. Users need to balance out rows or columns completely to match the total on the top of the column. An error is shown to the user on the page and on the home page if the allocation is not balanced.

Also, allocation is restricted by levels such that a resource cannot be moved from “SSC” to “Non SSC”, similarly, a top down approach is followed in SSC, such that a resource cannot be moved from Global site to Regional site and from Regional site to Local site but vice versa can be done.

### Site allocation

The Site Allocation screen allows users to manage resource distribution across various sites at a functional level. It displays a table with columns for Baseline FTEs and Target FTEs, segmented into Local, Regional, and Global categories. Users can view and adjust the allocation percentages for different sites such as Atlanta, Munich, and Berlin. The interface includes options to rename or create new scenarios and toggle between 'In-house' and 'Outsourced' views. This screen helps users ensure that the total allocation for each site sums to 100%, facilitating effective resource planning.

The Site Allocation screen displays a detailed table for managing resource distribution across various sites, focusing on functional levels. It includes columns for Baseline FTEs and Target FTEs, segmented into Local, Regional, and Global categories. Users can adjust allocation percentages for different sites, such as Atlanta, Munich, and Berlin, ensuring the total allocation for each site sums to 100%. The interface allows scenario management with options to rename or create new scenarios and toggle between 'In-house' and 'Outsourced' views. This screen aids in precise resource planning by providing a granular view of site-specific allocations.

The site allocation screen is similar to the resource allocation screen but this is used to determine the target resource allocation on a function level for each site. By default . the allocations are predefined based from the “Site Selection” page. The user can change the distribution, however the total for each site (sum of Local, regional and global) must be equal to 100%.

This view is divided between the “Insource” and “Outsource” resources.

## One off cost assumptions

The one off cost assumptions are used to review the cost implications occurring from the allocations in site selection and site allocation pages. It is used to define the timelines and cost implications to implement the plan.

### Transition costs

The 'Transition costs' screen allows users to define and manage the expected period for implementing process improvements, divided into three phases: Ramp up, Pilot, and Hyper care. It features a toggle for enabling detailed calculations and options to rename or create new scenarios. The main section includes a table detailing each phase's duration, retention bonus, percentage of legacy and new team members retained, number of FTEs involved, and associated transition costs. This screen helps users plan and calculate the total transition costs based on assumptions from previous pages, providing both a summary and detailed view for each phase.

The 'Transition costs' screen provides a detailed view of the transition phases for process improvement, focusing on specific functions such as Finance, HR, IT, Logistics, and Operations. It includes a comprehensive table that outlines the start of transformation, number of months, percentage of legacy team retained, and transition costs for each phase: Ramp up, Pilot, and Hyper care. The screen also displays optional details like the number of FTEs created or retained and retention bonuses. This view allows users to manage and adjust assumptions for each function, facilitating precise planning and cost calculation for the transition process.

“transition costs” screen is used to define the expected period to implement the overall process improvement. The plan is divided into three phases. Time duration defined for these three phased forms the total duration of the process improvement plan. This screen is divided into a summary and detailed view. Summary view provides an aggregated view for the three phases. The detailed view provides the details for each phase at a taxonomy level. This view allows the user to plan each phase individually for each taxonomy levels. The costs in this view are calculated from the assumptions defined in the previous assumption pages.

### Severance costs

The 'Severance costs' screen in the Shared Services section displays a table summarizing severance cost assumptions for a selected scenario, such as 'Restructuring, Q3 2025'. Key UI components include a toggle for enabling detailed calculations, options to rename or create new scenarios, and a table showing severance costs by phase. The table includes columns for the number of months of salary per impacted employee, the number of people impacted, and severance costs across different phases like Ramp-up, Pilot, Hypercare, and After care, culminating in a total severance cost. This screen helps users estimate severance costs associated with changes in resource allocation.

The 'Severance costs' screen in the Shared Services section provides a detailed table of severance cost assumptions for various countries under the scenario 'Restructuring, Q3 2025'. Key UI components include columns for the number of months/years of service, voluntary attrition rates, and average years of service in the baseline. The table also breaks down severance costs by phase, such as Ramp-up, Pilot, Hypercare, After care, and PI, with a total severance cost for each country. This screen allows users to analyze severance costs at a granular level, facilitating informed decision-making regarding resource allocation changes.

“Severance costs” view provides the estimated severance to be paid in different phases due to the changes in resource allocation.

In the high level view , it is shown as an overall aggregated value while the detailed view shows the cost at a site level. However, only those sites are shown which are actually getting impacted.

The “Average years of service” column is populated from the baseline data. However if the years of service is not available then the user can provide the years from their end.

### Other one-off costs

The 'Other one-off costs' screen in the Shared Services section displays a table for managing assumptions related to employee costs during the implementation phase. Users can view and edit assumptions such as 'Employee setup cost' and 'Hiring cost,' with associated values for each phase: Ramp-up, Pilot, Hypercare, and After care. The table provides a breakdown of costs per phase and calculates total costs. Controls for enabling detailed calculations, renaming, and creating new scenarios are available, allowing users to customize and analyze cost assumptions effectively.

The 'Other one-off costs' screen in the Shared Services section provides a detailed view of employee-related costs during the implementation phase. It features a table displaying costs by country, including 'Employee setup costs' and 'Hiring costs' with specific values for each phase: Ramp-up, Pilot, Hypercare, and After care. The table also shows total costs for each country. Users can enable detailed calculations and manage scenarios with options to rename or create new ones. This screen helps users analyze and adjust cost assumptions at a granular level, facilitating precise financial planning.

This view defines “Other” cost related to employees which are one off during the implementation phase. It has a “High level” view that shows the cost at an overall aggregated level. The detailed view shows the split of “other” costs at a country level and during each phase

## Output

The output screens provide the final calculate values based on the assumptions defined. All of these views are read only views and only for reporting purposes. No changes to the data or assumptions can be made from here. Filters implemented on any of the views will also be implemented on all the other Output views.

The 'SSOI: Analysis output' screen provides a summary of various reporting views available for analyzing labor cost optimization and workforce dynamics across multiple sites. It features six main cards: 'Savings and FTE evolution', 'Annual run-rate savings', 'FTE Impact overall view', 'FTE Shifts', 'One-time cost overview', and 'Calendar view'. Each card includes a brief description and an arrow indicating navigation to detailed reports. This screen helps users access read-only reports to track savings, FTE evolution, and implementation impacts, with filters applied consistently across all views.

### Savings and FTE evolution

The 'Savings and FTE evolution overview' screen displays a comprehensive summary of financial savings and changes in Full-Time Equivalents (FTEs) across different sites. Key UI components include dropdown filters for Function, Process, and Sub-process, which allow users to refine the data view. The screen presents financial metrics such as Baseline Cost, Total Savings, Labor Arbitrage, Process Improvement, and One-off Cost. Below these metrics, a detailed table outlines the evolution of FTEs, showing Baseline FTEs, FTEs at full potential, Net changes, Roles reduced, and Roles added. This view helps users analyze cost savings and workforce changes effectively.

This view provides an overall aggregated view of the savings in terms of money value and change in FTEs across sites. Filters from this page are carried forward to all the other screens.

### Annual run-rate savings

This view is a deep dive view for the money savings reported in the previous view. It provides breakdown of savings at a function level. Users can view the savings for In-house/outsourced or All resources.

The 'Annual run-rate savings' screen provides a detailed breakdown of financial savings at a functional level. It features dropdown filters for Function, Process, and Sub-process, allowing users to customize the view. The screen displays key metrics such as Baseline Cost, Total Savings, Labor Arbitrage, and Process Improvement, with values prominently shown. A 'Functions breakdown' section lists various business functions like Finance, HR, IT, and more, with corresponding savings figures. Users can toggle between In-house, Outsourced, and All resources to analyze savings distribution effectively.

### FTE impact overall view

The 'FTE impact overall view' screen provides a comprehensive analysis of Full-Time Equivalent (FTE) impacts across various functions. It includes dropdown filters for Function, Process, and Sub-process, allowing users to customize the data view. Key metrics displayed are Baseline FTE, FTE at full potential, Net changes, Roles reduced, and Roles added, with numerical values for each. A detailed breakdown by function, such as Finance, HR, and IT, is shown, highlighting specific FTE numbers and changes. This view helps users assess the current state of FTEs and understand the impact of changes at different taxonomy levels.

The 'FTE impact overall view' screen provides a detailed breakdown of Full-Time Equivalent (FTE) impacts, focusing on the current state of FTEs across various functions. It features dropdown filters for Function, Process, and Sub-process, allowing users to refine the data displayed. Key metrics include Baseline FTE, FTE at full potential, Net changes, Roles reduced, and Roles added, with specific numerical values for each. A tooltip provides additional context about role changes within functions. This view helps users analyze the impact of organizational changes on FTEs, offering insights into potential role adjustments and workforce optimization.

This view is similar to the view before but reports on the current state of FTEs instead of the money value. This view also reports breakdown at taxonomy levels.

### FTE shifts

The “FTE shifts” view reports the changes in FTEs from the Baseline value to the Target value at taxonomy level for each site. The user can view the values at an aggregated level by site types or further drill down to a site level.

The 'FTE shifts' screen displays a detailed report of Full-Time Equivalent (FTE) changes from Baseline to Target values at various taxonomy levels for each site. Users can filter the data by Function, Process, and Sub-process using dropdown menus. The table presents Baseline and Target FTEs, segmented into Local, Regional, and Global categories, with expandable sections for detailed views. Tabs allow users to toggle between In-house, Outsourced, and All FTEs. This screen aids users in analyzing workforce shifts and planning resource allocation effectively across different site types.

### One-time cost overview

This view provides a detailed view of the One time costs breakdown reported in the first view at a taxonomy level and split by cost types.

The 'One-time cost overview' screen displays a detailed breakdown of one-time costs at a taxonomy level, categorized by cost types such as transition, severance, and additional costs. Users can filter the data by function, process, and sub-process using dropdown menus. The main panel shows total one-time costs prominently, with individual cost categories listed alongside. A 'Functions breakdown' section on the left provides a detailed view of costs associated with specific business functions like Finance, HR, IT, and more. This screen helps users analyze and understand the distribution of one-time costs across different business areas.

### Calendar view

The calendar view allows the users to view the changes in FTEs and savings in each month of the process improvement implementation. The values are reported with breakdown at a taxonomy level. Users can view at the lowest granularity or at an aggregated level.

The Calendar view screen displays a detailed breakdown of Full-Time Equivalents (FTEs) and savings over a six-month period, categorized by taxonomy such as Finance, HR, and IT. Users can adjust the level of granularity and select the month range using dropdowns and increment controls. The table presents metrics like Total # of FTEs, Gross Savings, Total one-off costs, and Net impact, with values shown for each month and a cumulative process total. This view helps users analyze monthly changes in FTEs and financial impacts at both detailed and aggregated levels.

### All data table

(Figma TBD)

This view provides a combined tabular view of the output values broken down at taxonomy level.

## Scenario management

SSOI calculations follow a top down approach. Changes made to an assumption or costs page has an impact on all the values in the pages coming after that page. However, there is no impact on assumptions/costs before that page. This has an impact on how the scenarios are managed for SSOI.

Scenarios in SSOI are global scenarios i.e a scenario create don one page is available on other pages as well. By default there will be a “Master” scenario which will have the original values and can not be edited.

Ex: If user creates a scenario “Scenario 1” on Benchmarking page , then when user moves to the “Site selection” page, they will see “scenario 1” already selected there. This scenario will be based on the values from the “scenario 1” on Benchmarking page. Similarly “Scenario 1” would be created for all the other pages in the sequence.

# Automation

# Cross-tool Integration

# GenAI

# Backlog

## Advanced

Level selection for non existent levels for an assessment: If a user decides to chose a level that does not exist for an assessment, they would get a popup saying the level doesn exist for the assessment and the user needs to define the level hierarchy and provide relevant data

## Good to have

### User roles

Define roles like Admin, COE User and Consultants having various levels of access. Admin can have access to any case. COE users will have access to a limited no of cases and consultants will have access to only their current active case

### Admin page

Page for admin users to control access of users, add/remove/modify users. Delete/wipe old case data. Access to usage logs for the app
