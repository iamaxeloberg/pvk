
## Project Report 2: Quantera.ai


      - Group DD1367 Software Engineering in Project Form
- Albinsson, Hjalmar - 050425-
   - Berglund, Elias - 050622-91
   - Käll Lindfors, Folke - 011203-
   - Lindström, Wilhelm - 040706-
   - Ranow, Eugen - 050717-
   - Severien, Carl - 040930-
- Strihagen, Eric - 040114-
- Öberg, Axel - 040902-
         - 2026-03-
- Group
- 1. Team Members Table of contents
- 3. Methodology 2 Defining the problem
- 4. Proposed Solution
- 5 Project Details & Requirements
   - 5.1 Business Requirements
      - 5.1.1 Data structuring for AI-driven investment decisions
      - 5.1.2 Cost-effective and accurate data retrieval
   - 5.2 Functional Requirements
      - 5.2.1 Document Import & Indexing
      - 5.2.2 Internal Search
      - 5.2.3 Data Query & Insights
      - 5.3 Non-functional Requirements
      - 5.3.1 Cost efficiency
      - 5.3.2 Reliability and Data Accuracy
   - 5.4 Engineering Requirements
      - 5.4.1 Data Pipeline
         - 5.4.1.1 Input Files and Data Preparation
         - 5.4.1.2 Marker - Document Conversion
         - 5.4.1.3 Temporary Storage and AI-Based Categorisation
         - 5.4.1.4 Finished Data Preparation (Indexing)
         - 5.4.1.5 API Layer - Prompt and Internal Search
         - 5.4.1.6 Improvements for the Data Pipeline
      - 5.4.2 Frameworks/Languages/Libraries
      - 5.4.3 Material
   - 5.5 Requirement Traceability Matrix
   - 5.6 Timeline & Milestones
- 6. Project Deliverables
- 8. Testing and validation
- 9. Future work


#### Group 14

## 1. Team Members Table of contents

#### Axel Öberg

Skills

1. Mission-critical software development testing
2. AML & CTF Analyst

Position: Data Scientist

Contact information:
Email: oebergaxel@gmail.com

Tel: +46 76 007 02 79

#### Carl Severien

Skills

1. Private Wealth Management

Position: Data Scientist

Contact information:
Email: calle.severien@gmail.com

Tel: +46 70 867 54 62

#### Elias Berglund

Skills

1. Game Logic Development
2. Graphic Design

Position: Data Scientist

Contact information:

Email: eliabe@kth.se
Tel: +46 73 244 42 02

#### Eric Strihagen

Skills

1. Communication & Management
2. Backend development
3. System-level development

Position: Full-stack Engineer

Contact information:

Email: eric.strihagen@gmail.com
Tel: +46 72 387 73 70


#### Group 14

#### Eugen Ranow

Skills

1. GPT-API Integration
2. 3D-Rendering/Digital visualization
3. Game Development in C#

Position: AI Engineer

Contact information:
Email: eugenr@kth.se, eugen.ranow2005@gmail.com

Tel: +46 72 152 58 58

#### Folke Käll Lindfors

Skills

1. Proficient in Python
2. Game Development

Position: Data Scientist

Contact information:
Email: folkekl@kth.se

Tel: +46 70 642 60 36

#### Wilhelm Lindström

Skills

1. Studies in Business and Economics
2. Basic AI projects with Open-AI-API

Position: AI engineer
Contact information:

Email: wilhelmlindstrom04@gmail.com
Tel: +46 73 369 24 74

#### Hjalmar Albinsson

Skills

1. Basic AWS exposure (limited hands-on)
2. Python/TensorFlow fundamentals; built a bare-bones AI stock analysis project.

Position: AI engineer
Contact information

Email: hjalmar.albinsson@gmail.com
Tel: +46 72 579 56 22


#### Group 14

## 3. Methodology 2 Defining the problem

Private equity and fund capital market firms generate and collect large volumes of data that

accumulate over time. However, there are currently limited efficient methods for these
organizations to internalise this data and systematically cross-reference it with both internal and

external data sources.

To address this problem, Quantera proposes developing a system that enables clients to manage
internal economic documents and datasets using AI to calculate, analyze, and present key

performance indicators (KPIs). The initial step is to design a minimal viable product (MVP) for a
Holistic Agentic Leadership (HAL) system. This concept responds directly to customer demand

for innovative solutions to efficiently interpret uploaded internal data.

The HAL agent is intended to function as a senior digital colleague, capable of cross-checking

internal and external economic documents to support informed decision-making. The primary
target users for this product are private and fund capital market firms.

## 3. Methodology

The team follows a Scrum-inspired development process, organizing work into sprints with tasks
distributed based on role and experience. Regular internal meetings are held for planning and

progress tracking, while client meetings have focused on clarifying requirements and aligning on
project direction. Communication is handled through Slack, Discord, and in-person meetings,

with all feedback documented for reference. GitHub is used for version control, and a shared
Google Drive stores all project material, including reports and meeting notes.

Within this phase, an iterative approach is applied, where components are tested and refined

based on internal evaluation before progressing to the next stage.

## 4. Proposed Solution

The proposed solution is a modular data indexing and retrieval pipeline designed to process

unstructured financial documents and make them queryable through a natural language interface.

Raw input documents in PDF or Excel format are placed in an input directory. These are
converted to Markdown using Marker, an open-source document processing tool. The resulting


#### Group 14

Markdown files are then analysed by a low-cost language model that extracts basic metadata,

primarily the company name and document category, which is stored in a SQLite database
alongside a reference to the Markdown file.

When a user submits a query, the system filters the SQLite index to retrieve only the Markdown

files relevant to that query. These are combined with a prompt and passed to Claude, which
generates the final response.

This approach was chosen after initial research into Reducto AI and other indexing frameworks
revealed that an open-source pipeline built around Marker would be more cost-effective and

easier to control for an MVP scope.

Once these prompts are fully functional and tested against manual and automatic verification of

the data and analysis. We will create an AI picker that, depending on the user input, selects one of
these sub AI agents and provides the data from the pre-defined prompts. Once this is completed,

we will expose a documented Python API to call these functions with a simple web interface to
review the data.

## 5 Project Details & Requirements

### 5.1 Business Requirements

#### 5.1.1 Data structuring for AI-driven investment decisions

Capital market firms generate and collect large amounts of data in their operations. Most of the
company's data is in an unstructured way and in different file formats such as PDF and CSV.

Currently, they have no proper way of indexing and analyzing large amounts of data, and LLMS
can't handle such large amounts of data in one prompt.

Quantera wants companies to base future decisions based on the data they have collected from
their past investments and future investments. Quantera, therefore, needs a way of structuring

data in formats such as markdown that enables LLMs to accurately analyze it for data-driven

decisions.

#### 5.1.2 Cost-effective and accurate data retrieval

Once the data is structured, we want to sort the data for efficient processing. Processing all the
documents simultaneously would neither be technically efficient nor financially viable due to the

high AI token cost and the risk of bad data accuracy. The business requires a reliable method to
categorize and sort this structured data, for example, by company ticker. Categorisation ensures

that the system filter retrieves relevant data chunks for any given analysis, and this targeted
retrieval will help companies or individuals to maintain low operation costs while guaranteeing

good precision on data output.

### 5.2 Functional Requirements

#### 5.2.1 FR1 Document Import & Indexing

The system shall support CSV, PDF, and Excel files as input formats for financial data. These


#### Group 14

files may contain portfolio information such as revenue, margins, cash flow, and other key
financial performance figures.

The system shall extract relevant financial information from the uploaded files and organise the
extracted data suitably for analysis and retrieval. The extracted data shall then be indexed within
the system to enable efficient search and query operations.

#### 5.2.2 Internal Search

For a given company name or topic, the system should be able to search across the indexed
internal dataset.

When a search query is submitted, the system shall return a list of relevant results from the
indexed dataset. These results may include financial records, document excerpts, or other relevant
internal information related to the query.

#### 5.2.3 Data Query & Insights

The system shall allow users to submit natural language queries and receive generated responses
based on indexed portfolio data. These responses shall be presented in a clear and understandable
format for the user. The core product functions are to search data and gather valuable information
for the user efficiently and simply.

_Figure 1: Use Case-Diagram, Shows the interaction between the primary actor: The Capital
Market Firm User and the core system functions._


#### Group 14

### 5.3 Non-functional Requirements

#### 5.3.1 Cost efficiency

As the system relies on external LLM API’s, one critical constraint is operational costs. The
system must optimize memory load and token usage by ensuring the database strictly filters and

retrieves only the most relevant Markdown chunks. Sending entire, unfiltered documents to the
high-capacity LLM is prohibited by design to maintain financial viability.

#### 5.3.2 Reliability and Data Accuracy

The data extraction and categorisation pipeline shall maintain high structural fidelity throughout
all processing stages. The Marker conversion and AI categorisation steps must correctly preserve

document structure and accurately tag company names and document types. The system has to
handle formatting anomalies in raw financial documents without crashing or producing corrupted

output.

### 5.4 Engineering Requirements

This section describes the technical implementation used to construct the indexing system for
financial documents. The system is designed to process heterogeneous financial data sources such
as PDF files and spreadsheet documents and transform them into a structured format suitable for
efficient retrieval and analysis.

The core implementation follows a pipeline architecture in which input files are processed
through several transformation stages before being indexed in a database. The indexed
information can then be queried through an API layer that combines database retrieval with large
language model prompts to generate responses.

The current implementation uses a lightweight database solution based on SQLite due to its
simplicity, portability, and suitability for a minimal viable implementation.

#### 5.4.1 Data Pipeline

The data pipeline defines the process through which raw financial documents are ingested,
processed, categorized, and indexed in the system. The pipeline described in this section
represents the Minimal Viable Product (MVP) implementation. Possible improvements and
extensions to the pipeline are discussed in _Section 4.3.1.6_. A graphical representation of the
pipeline is included in _Figure 1_ to illustrate the overall architecture and the interaction between
system components. The pipeline contains both internally implemented components and
outsourced components, such as third-party parsing tools and AI models.

At a high level, the system workflow follows the structure below in _Figure 1_ :


#### Group 14

_Figure 2: Flowchart of the entire data pipeline_

The system separates data preparation, indexing, and query generation, allowing each stage to be
improved independently in future iterations.

##### 5.4.1.1 Input Files and Data Preparation

The pipeline begins with a directory containing raw input documents (DP1). These documents
primarily consist of financial data sources such as PDF reports and Excel spreadsheets. They may
contain structured or semi-structured financial information. The input folder acts as the entry
point for the pipeline, from which documents are automatically detected and processed. The
objective of this stage is simply to gather and prepare documents for transformation in subsequent
steps.

##### 5.4.1.2 Marker - Document Conversion

The next stage in the pipeline uses the external document processing tool Marker to convert the
input files into Markdown format (DP2). This step is outsourced to a third-party tool due to the


#### Group 14

complexity involved in reliably extracting structured information from PDF and spreadsheet
documents. The conversion produces Markdown files that retain the logical structure of the
original documents, including headings, tables, and textual content. Markdown is selected as an
intermediate representation because it is lightweight, human-readable, and well-suited for further
processing by language models.

##### 5.4.1.3 Temporary Storage and AI-Based Categorisation

After the document conversion stage, the generated Markdown files are stored in a temporary
processing directory (DP3). This directory functions as an intermediate step in the pipeline where
the converted documents are prepared for indexing. At this stage, a **low-cost language model**
(DP4) is used to analyse the Markdown content and extract basic metadata describing the
document. This is done by providing the language model with the Markdown content as well as a
master prompt (MP1) containing our database structure and the objective (MP2) to identify and
create categories. The purpose of this step is to generate structured attributes that can later be
used for indexing and retrieval.

The model focuses on identifying the primary entity or company referenced in the document and
relevant categories describing the document content. For example, the AI may produce outputs
from a company ABC's financial report, such as:

```
● Company: Company ABC
● Categories: financial report, earnings, market analysis
● Markdown File Path: /financial_reports/abc_quarter_1.md
```
The extracted metadata is then stored in a SQLite database (DP5), together with a reference to the
corresponding Markdown file stored on disk. Rather than storing the full document within the
database, the system maintains the Markdown files in the filesystem and uses the database as a
lightweight indexing layer.

This design allows the database to store structured attributes such as company name, document
categories, and file paths while keeping the database size small and ensuring efficient document
retrieval. The SQLite database, therefore, functions as a searchable index over the processed
documents, enabling efficient lookup during later query operations.

##### 5.4.1.4 Finished Data Preparation (Indexing)

Once categorisation is completed, the processed Markdown content and associated metadata are
stored permanently in the SQLite database.

At this stage, the documents are considered fully indexed and ready to be queried. Therefore, the
database contains a Markdown representation of each document with extracted categories and
associated entities (e.g., company name) that reference the original file. This structured storage
enables efficient retrieval during later query operations.

##### 5.4.1.5 API Layer - Prompt and Internal Search

The final stage of the system is an API layer responsible for handling user queries. As mentioned
previously, the system should have a well-defined API. This API will be defined in Python and be
callable from different contexts, enabling it to be used from the terminal or from the web, which
will be more applicable for further work if a dashboard is implemented. When a request is
received through our API system, the system performs two processes, which can be seen in
_Figure 2_ below.


#### Group 14

_Figure 3: Flowchart of the API layer_

When a prompt is handed to the API, the first process is to retrieve the relevant Markdown
content. This is done by filtering our SQLite database containing companies, categories, and
filepaths to Markdown files relevant to answering the prompt with a language model. To
efficiently identify relevant files, we will feed the language model the user prompt (AL1), a
predefined master prompt (MP1), a fetch data prompt (MP3), and the content of the internal
SQLite database. Thereafter, the selected filepaths will be forwarded to the second process (AL2).

The master prompt plays an important role in this step. It provides a stable description of the
system’s indexing structure and helps the retrieval step interpret the stored data consistently.
Rather than sending the entire database to the final model, the system first narrows the context to
the files most likely to be relevant (AL3). This reduces unnecessary token usage and improves the
likelihood of generating a more focused response.

The second step utilises the retrieved Markdown data, which is then combined with the user
prompt and another master prompt focused on specifying the query's goal. This is then sent to a
higher-capacity language model (RG1), and then returned to the user via the API (RG2). The


#### Group 14

language model used for this final reasoning step will be iteratively tested and changed to balance
between the resulting data, costs, and speed. The first iteration will use Claude as a reasoning
model. A prototype of the end terminal's usage is shown in _Figure 3_.

_Figure 4: A prototype of the API-layer input and output from the terminal script_

By retrieving only relevant documents from the database before interacting with the
higher-capacity language model, which is often more expensive, the system reduces unnecessary
token usage and improves the relevance of generated responses.

##### 5.4.1.6 Improvements for the Data Pipeline

The MVP implementation includes document ingestion, Markdown conversion, metadata
extraction, SQLite indexing, and an API-based retrieval and query layer. The following
improvements have been identified but are deliberately left outside the current MVP scope.

One key improvement is the introduction of document chunking and semantic search. Instead of
storing entire documents as single entries, documents can be divided into smaller information
segments (chunks). These chunks could then be indexed individually, making retrieval more
precise and reducing the amount of irrelevant context sent to the language model. This is
especially useful for very large documents that contain different kinds of information, while only
a specific part is useful to the user.

A second improvement is the introduction of external source integration, allowing the system to
combine internal document retrieval with selected web-based or third-party data sources.
However, this has been moved to future work in the current report in order to avoid unnecessary
architectural complexity at this stage.

A third improvement is the implementation of a dashboard layer for visual interaction with the
indexed data and generated outputs. This was also considered in the earlier project scope, but has
now been postponed to future work. The current report instead prioritises the internal pipeline
and indexing architecture as the core engineering contribution and priority for the minimal value
product.

Overall, these improvements remain consistent with the chosen architecture, since the current
design already separates ingestion, indexing, retrieval, and generation into distinct stages that can
be extended independently.


#### Group 14

#### 5.4.2 Frameworks/Languages/Libraries

As the project is centered around an API first architecture and data-driven intelligence, we have

chosen Python as the primary language throughout the entire backend and core logic. Python will
simplify development, testing, and maintenance, while also aligning well with the project’s focus

on data processing, AI integration, and agent-based workflow.

Markdown is used as the system’s intermediate document format because it is lightweight,
human-readable, and well-suited for further automated processing. To generate this format, we

use the Marker library to convert source documents into Markdown while preserving important

structural elements such as headings, tables, and textual hierarchy. This makes the converted files
easier to index, analyse, and reuse in later stages of the pipeline. As an alternative to Marker,

Reducto AI could also be considered for document conversion, depending on extraction quality,
cost, and integration requirements.

Language models are used in multiple stages of the system pipeline. In the earlier processing
stage, a lower-cost model, such as DeepSeek or a similar lightweight alternative, can be used for

metadata extraction and document categorisation in order to reduce operational costs. In the later
prompting stage, where retrieved Markdown content is combined with the user query to generate

a final response, Claude is used due to its stronger reasoning and synthesis capabilities. This
division allows the system to balance cost efficiency with response quality by reserving the more

capable model for the final stage of query handling.

For persistence, we will use SQLite as the database, which is sufficient for the scope of 1-
companies and 1-3 years of monthly data, and it enables fast prototyping with minimal overhead.

The system will store structured portfolio data as well as indexed metadata needed for search and
retrieval.

In the future, we plan on implementing the Python web framework Flask for the backend. Flask

provides a lightweight foundation suitable for building a clean REST-based API. **React** for the
frontend, primarily the dashboard, an open-source JavaScript library for building

component-based user interfaces. React’s architecture supports the SoC principle required by the
project, improving modularity and reducing complexity and overlap. Since the project follows an

API-first design, the React frontend will be reliant on the Flask REST API for all functionality,

and will communicate through HTTP requests to endpoints, receiving JSON responses that are
rendered in the UI.

#### 5.4.3 Material

To complete the project, we need a combination of hardware, software, and cloud services.

Hardware: We will use personal computers for development and testing. For heavier workloads

such as embedding generation, we will rely on cloud compute when needed, available through the
provided NVIDIA Inception Portal.

Software: The work relies on access to a shared cloud development environment and version

control infrastructure. We will use a GitHub repository to manage project code, and Slack will be


#### Group 14

```
used for team coordination and communications. For the indexing, we will use a combination of
Marker and our own developed solution.
```
### 5.5 Requirement Traceability Matrix

```
Based on the business requirements, we have created a requirements traceability matrix to
monitor the connections between each business requirement, the design, and functional
implementation, as well as the prioritization. Non-functional requirements are included separately
at the bottom of the matrix, as they apply across multiple functional requirements rather than
mapping directly to a single business requirement. ( Figure 4 )
```
**BR ID Business
Requirement**

```
FR ID Functional Requirement Design and
Engineering
(How)
```
```
Priorit
y
```
BR1 A system
capable of
ingesting,
structuring,
and indexing
large volumes
of financial
data.

```
FR1 Support import, extraction, and
indexing of monthly portfolio
data from CSV and Excel files.
The system shall organize
extracted financial information
(including revenue, margins,
and performance figures) into a
defined set of structured
entities, such as funds, portfolio
companies, and specific
financial metrics.
```
```
Marker
converting to
markdown →
Low-cost LLM
extracts the
company name
and category
before retrieval
→
Indexed in
SQLite
```
```
High
```
BR2 Cost-effective
and accurate
data retrieval

```
FR2 The deep search function shall
enable users to search across
processed internal data sources
such as company summaries.
For a given company or topic,
the system shall return a list of
relevant hits based on the
structured data entities and
indexed documents.
```
```
SQLite filtered by
company and
category before
retrieval →
Relevant
Markdown files
passed to Claude
via master prompt
```
```
Mediu
m
```

#### Group 14

BR2 Cost-effective
and accurate
data retrieval

```
FR3 The system shall allow users to
submit natural language queries
and receive generated responses
based on indexed portfolio data,
presented in a clear and
understandable format
```
```
Retrieved
Markdown
combined with
user prompt and
master prompt
passed to Claude
for final response
```
```
High
```
###### NFR

###### ID

```
Non-
Functional
Requirement
```
```
Design and Engineering Priority
```
NFR1 Cost
efficiency

```
SQLite filtering ensures that only the
relevant chunks are sent to the LLM
```
```
High
```
NFR2 Reliability
and Data
Accuracy

```
Categorisation validated by comparing
pipeline output against manually
pre-written answers
```
```
High
```
```
Figure 5
```

#### Group 14

### 5.6 Timeline & Milestones

### QUANTERA · GROUP 14 · PROJECT

### TIMELINE

###### TASK DEADLINE STATUS ACCOUNTLE AB DONE

###### ^ INDEXING^ PIPELINE^

#### 1 ·^ Input^ folder^ (PDF^ /^ Excel)^ Ongoing^ Building^ All^

#### 2 ·^ Marker^ →^ convert^ to^ Markdown^27 Mar^ Building^ Folke^ /^ Eugen^

#### 3 ·^ Low-cost^ AI^ →^ categorization^27 Mar^ Urgent^ Hjalmar^ /^ Axel^

#### 4 ·^ SQLite^ →^ indexed^ storage^27 Mar^ Urgent^ Elias^ /^ Carl^

```
5 · API Layer → prompt + Claude →
```
#### output 27 Mar^ Urgent^ Eric^ /^ Wilhelm^

#### 6 ·Testing^ and^ verification^03 Apr^ Urgent^ Axel^ /^ Carl^

###### ^ REPORTS^ &^ DEADLINES^

#### Report^1 Submitted^ ✓^ Done^ All^ ✓^

#### Indexing^ research^ Done^ ✓^ Done^ All^ ✓^

#### Report^2 20 Mar^ 19:00^ Urgent^ All^

#### Seminar^ presentation^13 Apr^ 12:00^ Upcoming^ All^

#### Half-time^ presentation^15 Apr^ 12:00^ Upcoming^ All^


#### Group 14

#### Report^3 15 May^ 19:00^ Planned^ All^

#### Final^ presentation^28 May^ 17:00^ Planned^ All^

_Figure 6_

The focus at the start of the project will be on researching current AI-indexing systems such as

Reducto and exploring different LLMs. This is for getting a broader understanding of the project
and how we will tackle the AI-indexing task. We had one kick-off meeting before Christmas to

get to know each other and to discuss their mission. They provided us with links to check out
different services that they use today, such as Epoch AI for benchmarking AI models, Crew AI

for building AI agents, Reducto, KIMI K2 (their primary LLM), and V7 Index Knowledge(their

competition).

After we have familiarised ourselves with AI-indexing, it is time for us to start coming up with a
plan on how we should implement the AI-indexing pipeline. The indexing research took longer

than expected. and made us aware of an open-source project that could help us with transforming
files to Markdown locally. This made the project take a turn, scrapping our earlier idea of

completely developing our own system. Instead, focus more on the pipeline where we will use a
low-cost AI for categorising the converted markdown files and then storing it and accessing the

relevant data for Claude to base its answer on.

We created a structured project plan in Excel for keeping track of important milestones and

deadlines. This is for making sure that we are progressing towards the goal and that everyone
knows what to do. And if we stumble across problems and delays, it is easy to see what will be

affected.

## 6. Project Deliverables

The deliverables for this project consist of both the functional software components that make up

the Minimum Viable Product (MVP) for Quantera, as well as the academic documentation.

#### 6.1 Software Artefacts & System Components

- **AI Indexing Pipeline:** A core backend service designed to take unstructured financial
    data (such as CSV, PDF, and Excel files), extract relevant information, and structure it
    into an indexed format (e.g., Markdown and SQLite) optimized for Large Language
    Models.
- **LLM Sub-agents:** Using LLM models as an analytical engine, integrated sub-agents
    should utilize the structured data to generate specific financial insights, track key
    performance indicators (KPIs), and automatically produce the data-driven briefings.
- **Accuracy and Relevance Assessment:** A formal evaluation delivered alongside the
    software to ensure system reliability. It demonstrates how the sub-agents' outputs have
    been tested and verified against expected financial metrics and manual baselines.


#### Group 14

#### 6.2 Academic Documentation

- **Report 1 (Planning & Organization):** Delivered in the initial phase, this report
    establishes the project's foundation. It details the structured project plan, the chosen
    development methods, initial risk analysis, and the preliminary project requirements set
    by the client.
- **Report 2 (Analysis & Design):** This report details the transition from conceptual
    requirements to technical solutions. It provides an in-depth breakdown of the functional
    and non-functional requirements and their connection to the business requirements. It
    outlines the specific frameworks and libraries used and presents a Requirement
    Traceability Matrix that maps business needs to the finalized system architecture.
- **Report 3 (Verification & Validation):** The final report will evaluate the finished MVP.
    It will detail the testing procedures, assess how well the system fulfills the initial
    requirements, summarize the results of the accuracy assessments for the AI sub-agents,
    and outline recommendations for future work.

## 7. Risk Analysis

This project includes several risks across software development, team coordination, and external
dependencies. Each risk has been evaluated based on probability and impact, and converted into a concrete
design decision to mitigate the risk.

```
Risk Probabilit
y
```
```
Impact Design Decision
```
```
Lack of communication
with the client
```
```
Moderate Moderate Created a Discord to provide easy access to company
stakeholders. Also provides documentation of
communication
```
```
Not receiving data for
indexing
```
```
High Seri ous Pipeline is constructed against a synthetic dataset made
to replicate real data, ensuring the system can be
developed regardless of the client delivering data.
```
```
Other courses are taking
more time than expected,
and overlapping with our
planning
```
```
Moderate Serious Very minimal MVP scope with a working indexing
pipeline and API being the required deliverables Also,
weekly check-ins to discuss current course load and
individual and short-term plan going forward to ensure
that everyone is on the same page.
```
```
Group members unable
to contribute due to
inexperience are
delaying certain
deadlines.
```
```
Moderate Moderate The pipeline is divided into independent modules with
clear ownership per stage. A member becoming
unavailable affects only their stage, and responsibilities
can be redistributed without rebuilding the system.
```

#### Group 14

```
Other courses overlap
with the project timeline
```
```
High Serious The MVP scope is deliberately minimal — a working
indexing pipeline is sufficient for client delivery.
Features beyond this are treated as future work,
reducing the risk of under-delivery.
```
```
Low-cost AI
categorisation returns
low accuracy on ticker
extraction, bottlenecking
the entire pipeline.
```
```
High Serious Categorisation is isolated from the rest of the process
and manually validated. Experiment with different
models and prompts until the desired accuracy is
found.
```
```
Generated final answers
show high variance with
different results in each
run with the same
question
```
```
High High Lower temperature for more consistent answers and
provide the desired output for the answer. Limit the
context window sent to the LLM.
```
_Figure 7_

## 8. Testing and validation

To validate that a requirement is fulfilled, we have created a table that associates each

requirement with a defined test criterion (acceptance criterion). All high-priority criteria (FR1,
FR2, FR3, NFR1, NFR2) must be met to consider that we have achieved an MVP(minimum

viable product).

## Testing & Validation

## Test ID Test Description

```
Linked
Requiremen
```
## t

## Deadline Acceptance Criterion

## T

```
Can the system process
CSV, Excel, and PDF files
```
## without crashing?

## FR1 27 Mar All^ three^ file^ types^ are^ errorsprocessed correctly^ without^

## T

```
Marker: Does marker
produce correct markdown
```
## files for the filetypes?

## FR1, NFR2 27 Mar Tables,^ text,^ and^ informationcorrect way^ are represented^ in^ a^

## T

```
Categorization: Does the
AI model extract correct
company names and
```
## categories?

## FR1, NFR2 27 Mar >90% correct identification of our sample companies

## T4 SQLite:retrieved^ Is^ data correctly?^ stored^ and FR1, FR2 27 Mar All^ indexed^ documentsand categoryare^ retrievable. by^ company^

## T

```
Can the system return
relevant results for a given
```
## company or topic query?

## FR2, NFR1 3 Apr Only relevant markdown files are passed to Claude.


#### Group 14

## T

```
Does the system return
correct answers to
```
## predetermined questions?

## FR3, NFR2 3 Apr At^ least^ 8/10^ correctquestions.^ answers^ on^ pre-determined^

## T7 What^ happensdocuments?^ with empty^ NFR2 3 Apr System returns an error message without crashing.

## T

```
What happens if the
marker file conversion
```
## fails?

## NFR2 3 Apr Systemaffecting^ logs^ the thefailure, rest ofskips the^ thepipeline.^ file^ without

_Figure 8_

## 9. Future work

One of Quantera’s main final requirements is to create a functioning AI voice-enabled chat

integrated into the dashboard. This is seen in our project as a future work possibility and will not

be a priority. This is done to ensure core functionality and accuracy before implementing new
additions that do not contribute to the main functionality of the project.

When time can be allocated to work on this, the voice-enabled chat should be able to capture

audio, convert it to text (STT), and send queries to the backend API. The backend should then
interpret this and provide an answer with the necessary details and analysis converted back to

speech (TTS), while still displaying it in the chat log on the dashboard. The added functionality is
required to also add the necessary documentation to make it accessible from a third party. The

minimum questions that the AI voice chat should handle are: “How is Company X doing?”, What
are the main risks in the portfolio?”, and “Any recent signals on Company X’s Sector?”.


