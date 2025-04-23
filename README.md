# Scientific Knowledge Extraction Ontology

This document outlines the general specification for the task of extracting scientific knowledge from peer-reviewed papers with a focus on Scientific Research: Methods, Opportunities, and Challenges.

Please see the `SKEO_extractor` folder for more information on the knowledge extraction tool.

## 1. Introduction

### 1a. The Business Imperative for Structured Scientific Knowledge

The rapid acceleration of scientific progress presents both unprecedented opportunities and challenges for businesses seeking competitive advantage through innovation. Scientific research produces millions of new contributions annually, creating a "flood of pseudo-digitized PDF publications" [1] that contains valuable insights but remains largely inaccessible. This burried knowledge represents untapped potential for product development, process improvement, risk management, and strategic planning. For the main explaination, the information embedded within narrative text is not readily machine-actionable, meaning that potentially valuable research insights cannot be efficiently searched, filtered, or analyzed in the context of specific business needs [1].

The business value of scientific knowledge depends fundamentally on the methods employed to generate it, the opportunities it reveals, and the challenges it addresses. Scientific methods, encompassing experimental designs, computational workflows, analytical procedures, and validation techniques, vary significantly across disciplines and directly affect the reliability and applicability of findings to business contexts [2]. Understanding these methods is crucial for businesses to assess the credibility, replicability, and real-world applicability of research claims before committing resources to implementation.

Equally important for business decision-making is a clear understanding of the opportunities and challenges identified within scientific literature. These represent potential innovation pathways and implementation barriers that directly affect return on investment, time-to-market, and competitive positioning. Opportunities include identified knowledge gaps that might translate to market gaps, research questions that could evolve into product features, and potential applications that may create new business models. Challenges encompass fundamental scientific hurdles, methodological limitations, and implementation constraints that impact commercialization timelines and resource requirements.

### 1b. Bridging Science and Business Through Structured Knowledge

Recognizing these business imperatives, a paradigm shift is underway from document-based scientific communication towards knowledge-based systems built upon structured, semantic representations [1]. This transformation is particularly vital for businesses that must rapidly translate scientific insights into actionable intelligence, competitive advantage, and measurable impact.

Structured knowledge systems enable businesses to:

1. **Accelerate Innovation Cycles**: Quickly identify relevant scientific advances and assess their business implications, reducing time from discovery to application
2. **Make Informed Investment Decisions**: Systematically evaluate the strength of scientific evidence, implementation requirements, and potential ROI of emerging technologies
3. **Mitigate Technical Risk**: Recognize potential implementation challenges, methodological limitations, and validation requirements before committing resources
4. **Identify Strategic Opportunities**: Discover untapped applications, novel combinations of technologies, or emerging markets suggested by scientific findings
5. **Optimize Resource Allocation**: Direct R&D investments toward scientifically promising areas with clear paths to commercialization

## 1c. Ontologies and Taxonomies: Enabling Modern AI Applications

The practical implementation of structured scientific knowledge relies heavily on well-designed ontologies and taxonomies. These frameworks are not merely academic exercises—they serve as the foundational infrastructure that enables modern generative AI systems to deliver actionable business intelligence from scientific literature.

In today's business applications, ontologies and taxonomies are powering:

1. **Domain-Specific AI Assistants**: Enterprise generative AI tools that understand scientific concepts within industry-specific contexts, translating complex research into actionable business recommendations
2. **Intelligent R&D Workflows**: Systems that automatically extract structured information from scientific papers, map methodological approaches to business requirements, and identify promising opportunities for product development
3. **Automated Technology Scouting**: Solutions that continuously monitor scientific literature, identifying emerging technologies relevant to specific business challenges while assessing their maturity and implementation requirements
4. **Evidence-Based Decision Support**: Tools that evaluate scientific claims based on methodological rigor, validation approaches, and reproducibility provisions, helping businesses distinguish between hype and substantiated innovations
5. **Market Intelligence Enhancement**: Applications that connect scientific advances to market trends, regulatory developments, and competitive activities, providing comprehensive strategic insights

Without structured representations like ontologies, generative AI systems struggle to extract meaningful patterns from scientific literature, often producing superficial analyses lacking the nuance and context needed for high-stakes business decisions. Well-designed ontologies enable these systems to understand the relationships between scientific methods, findings, opportunities, challenges, and business implications—transforming raw information into strategic intelligence.

This report proposes a Scientific Knowledge Extraction Ontology (SKEO) specifically designed to bridge the gap between scientific knowledge and business application. By integrating three critical dimensions—scientific methods, opportunities, and challenges—with explicit business relevance properties, this framework provides the structured foundation necessary for organizations to systematically extract value from scientific advances, identify actionable opportunities, anticipate implementation barriers, and ultimately translate research findings into market impact and competitive advantage.

## 2. Foundational Concepts

### 2.1 Defining Ontology and Taxonomy

In the context of information science and knowledge engineering, **ontology** refers to a formal, explicit specification of a shared conceptualization [14]. It goes beyond a simple dictionary or glossary by defining a set of concepts (classes), their properties (attributes), the relationships between concepts, and potentially axioms or constraints that govern these elements within a specific domain [14]. Ontologies aim to capture the structure of knowledge, enabling unambiguous communication, data integration, automated reasoning, and enhanced problem-solving capabilities [4]. They provide a machine-readable representation of a domain, facilitating tasks like semantic search, data validation, and knowledge discovery [4].

While rooted in philosophical inquiries into the nature of being and reality (metaphysics) [13], applied ontologies focus on creating practical, computational models of specific subject areas [14]. The development of ontologies is recognized as a fundamental step in the formalization of science, particularly for describing complex domains like scientific experiments [11].

A **taxonomy**, in contrast, is primarily a classification system that organizes concepts or entities into a structured hierarchy, typically based on 'is-a' or 'part-of' relationships [19]. It provides structured names and definitions used to organize information and knowledge, making knowledge within documents clearer and more usable [20]. Taxonomies are fundamental components of information architecture and knowledge management [20].

Within research contexts, ontologies serve multiple purposes. They help structure complex information domains [16], reduce ambiguity, inconsistency, and incompleteness in descriptions (e.g., in requirements engineering [17]), facilitate the analysis and comparison of domain knowledge [19], and enable interoperability between different systems or datasets [20].

### 2.2 Defining Key Scientific Process Terms

Several terms are central to describing scientific processes, often with overlapping meanings. Establishing clear definitions is crucial for the proposed ontology:

* **Method / Procedure / Plan:** This refers to the specification, recipe, protocol, or plan detailing how a particular scientific activity or set of activities should be carried out [6]. It represents the intended design or workflow. This concept aligns with the Method class in the Scholarly Ontology (SO) [22], the prov:Plan concept from the PROV Ontology often used as a basis for workflow descriptions like wfdesc:WorkflowTemplate in the Research Object (RO) suite [23], and the ExperimentalDesign component in the EXPO ontology [8].

* **Activity / Execution / Experiment:** This denotes the actual performance or enactment of a method, procedure, or plan [6]. It is the realization of the intended design in practice. This corresponds to the Activity class in SO [22], the wfprov:WorkflowRun concept in the RO suite [23], and the overarching concept of a ScientificExperiment (including its actions and results) in EXPO [8].

* **Workflow:** Often used in computational contexts, a workflow represents a structured sequence of connected tasks or processes designed to achieve a specific goal, frequently involving data flow between steps [25]. Workflows typically consist of processes (tasks, steps) and data links defining dependencies [24]. While prevalent in bioinformatics and other computational fields [23], the concept of a structured sequence of tasks is broadly applicable to many scientific procedures, including laboratory protocols and clinical processes [24].

* **Research Problem (RP):** The core issue, question, phenomenon, or unsatisfactory situation that the research fundamentally aims to address, understand, explain, or solve [1]. It represents the central challenge motivating the entire study and provides the context for the methods, results, and conclusions.

* **Research Question (RQ):** A specific, focused, interrogative statement that the research aims to answer directly [13]. It serves to operationalize the investigation of a broader ResearchProblem or KnowledgeGap, providing clear direction for the study's methodology and analysis.

### 2.3 Philosophical Context (Ontology/Epistemology)

The choice and application of a scientific method are not solely determined by technical considerations. They are often influenced by the researcher's underlying philosophical assumptions about the nature of reality (**ontology**) and how knowledge about that reality can be acquired (**epistemology**) [2]. These assumptions form a **research paradigm**, which acts as a lens shaping the researcher's worldview and guiding their methodological choices [2].

For instance, a researcher adopting a *realist* ontology (believing in an objective, external reality) might favor quantitative methods aiming for objective measurement and minimization of bias, as often seen in experimental research [2]. Conversely, a researcher with a *relativist* ontology (viewing reality as subjective and context-dependent) might employ qualitative methods to explore diverse interpretations and experiences [2].

Understanding these foundational beliefs provides crucial meta-context for interpreting why a particular method was chosen and how its results are framed [2]. The proposed ontology should, therefore, ideally accommodate the capture of this high-level paradigmatic context, recognizing that the 'how' of science is often intertwined with beliefs about 'what is' and 'what can be known'.

## 3. Analysis of Existing Frameworks for Scientific Research

### 3.1 Scholarly Ontology (SO)

SO aims to model general scholarly practices, drawing inspiration from business process modeling and Activity Theory [28]. Its core strength lies in the clear distinction between Method (the procedure or plan) and Activity (the actual execution) [6]. SO employs four perspectives—Activity, Procedure, Resource, and Agency—to capture different facets of scholarly work [22]. It defines key concepts such as Actor, Goal, Tool, Input, Output, Step, and contextual elements like Discipline and School of Thought [22]. This structure allows for modeling who does what, how, why, and with what resources [6]. However, while providing a useful general framework, SO may lack the specific granularity required for detailing complex experimental or computational procedures compared to more specialized ontologies like EXPO or the RO suite [6].

### 3.2 Research Object (RO) Suite

The RO suite focuses on aggregating and describing digital research artifacts, particularly computational workflows, their associated data, and provenance information, to enhance sharing, preservation, interpretation, and reuse [3]. It comprises several key ontologies built upon standards like ORE, AO, and PROV-O [23]:

* **WRO (Workflow Research Object ontology):** Defines the basic structure for aggregating resources (ResearchObject, Resource, Annotation) [3].
* **wfdesc:** Describes workflow templates (wfdesc:WorkflowTemplate, wfdesc:Process, wfdesc:Parameter) providing an abstract representation of the workflow structure [23].
* **wfprov:** Captures provenance of workflow executions (wfprov:WorkflowRun, wfprov:ProcessRun, wfprov:Artifact), linking execution details back to the template [23].
* **ROEvo:** Models the evolution and versioning of Research Objects [23].

The strength of the RO suite lies in its robust handling of computational workflows and their provenance, directly addressing reproducibility concerns in data-intensive science [3]. Its workflow-centric nature [24], however, means it may not inherently capture the nuances of non-computational experiments (e.g., specific laboratory techniques, sample handling, field observations) as deeply as ontologies designed for broader experimental contexts like EXPO or domain-specific ones like EFO [31].

### 3.3 EXPO (Ontology of Scientific Experiments)

EXPO was developed to formalize generic concepts applicable to experiments across all scientific disciplines, based on the premise of a unified scientific experimentation process [8]. It links the Suggested Upper Merged Ontology (SUMO) with subject-specific experiment ontologies [8]. Key concepts include ScientificExperiment (with types like Galilean, Baconian, Physical, Computational), ExperimentalDesign, ExperimentalGoal, ExperimentalHypothesis, ExperimentalObject, Equipment, ExperimentalActions, ExperimentalResults, and ResultError [8]. EXPO's strengths are its domain independence, explicit modeling of experimental goals and hypotheses, and its attempt at theoretical grounding based on the philosophy of science [8]. However, its generality might require significant extension for practical application within specific domains [8]. Its development also appears less active in recent years compared to the RO suite [10].

### 3.4 SemSur

Developed for representing the content of survey articles, SemSur provides core classes for Research Problem, Approach, Implementation, Evaluation, Challenge, and Limitation [2]. Its strength lies in explicitly modeling challenges and limitations associated with specific approaches or implementations. However, its focus is primarily on the context of literature reviews rather than primary research.

### 3.5 Open Research Knowledge Graph (ORKG)

The Open Research Knowledge Graph focuses on structuring individual research contributions to enable comparison, typically organized around a Research Problem and detailing associated methods, results, and other contribution data [1]. It utilizes crowdsourcing and templates to populate the graph. While powerful for comparison, its core structure might lack the granularity needed to capture different types of opportunities and challenges explicitly.

### 3.6 Problem Assessment Ontology (PAO)

PAO offers a rich semantic model for *assessing* the nature and significance of Research Problems, considering actor perspectives, context, barriers, scale, and tractability [21]. This provides valuable dimensions for understanding Research Problems, though its primary focus is assessment rather than classification of types of opportunities/challenges across diverse papers.

### 3.7 Conceptual Frameworks Literature

Conceptual frameworks, as discussed in educational and social science research literature, provide a structure for explaining the rationale, key variables, and expected relationships within a study [21]. They are typically developed by researchers based on literature reviews and prior knowledge [32]. Essential components include the Research Question, definition of Variables (Independent, Dependent, Mediating, Moderating, Control), postulated Relationships between variables, underlying Assumptions, and the Theoretical Basis or models informing the study [21].

Conceptual frameworks excel at articulating the 'why' (theoretical grounding, significance) and the 'what' (variables, hypotheses) of the research [21], aspects often underspecified in purely procedural descriptions. They serve as a roadmap connecting theory, research questions, and methods [21].

### 3.8 Other Relevant Models

Domain-specific or purpose-specific taxonomies and ontologies further illustrate the need for structured method description. Examples include:

* **BrainMap Taxonomy:** A hierarchical keyword system for coding neuroimaging experimental metadata [19].
* **Experimental Factor Ontology (EFO):** Integrates concepts from multiple biomedical ontologies to describe experimental variables [31].
* **Fault Taxonomies:** Classify potential errors in scientific workflow execution [25].
* **Clinical Workflow Taxonomies:** Structure common clinical tasks and workflows to support CDS implementation [26].

### 3.9 Synthesis and Gaps

This review reveals that existing frameworks offer valuable components but possess distinct specializations. SO provides a general model for scholarly actions, RO excels in computational workflow representation and aggregation, EXPO offers a generic structure for experimental logic, SemSur explicitly models challenges and limitations, ORKG focuses on contribution comparison around Research Problems, and conceptual frameworks articulate the theoretical rationale and core variables.

A significant gap exists in integrating these diverse perspectives into a single, comprehensive ontology. Such an ontology needs to capture the entire lifecycle of scientific research: from its philosophical and theoretical grounding, through hypothesis formulation and study design, detailing procedures (both computational and physical), data collection and analysis techniques, to validation steps, limitation reporting, and reproducibility provisions, while also structuring the opportunities and challenges that drive the research forward.

A recurring and fundamental distinction across SO, RO, and EXPO is the separation between the *plan* or *design* (Method, Template, Experimental Design) and the *execution* or *performance* (Activity, Run, Experiment) [8]. Maintaining this distinction is crucial for modeling both the intended methodology and its actual application, including any deviations or specific runtime parameters.

## 4. Scientific Knowledge Extraction Ontology

Based on the analysis of existing frameworks and the identified need for a more comprehensive model, this section proposes an integrated ontology, termed the Scientific Knowledge Extraction Ontology (SKEO), designed to systematically represent scientific methods, opportunities, and challenges.

### 4.1 Overall Structure and Rationale

SKEO adopts a modular, layered structure, organized around three main branches:

1. **Scientific Method Components**: Focused on representing the procedural and methodological aspects of research
2. **Scientific Opportunity Components**: Capturing the forward-looking, gap-filling, and application-oriented aspects
3. **Scientific Challenge Components**: Describing the obstacles, difficulties, and limitations inherent in research

The structure aims for compatibility with established upper ontologies like BFO (Basic Formal Ontology) or SUMO [8] for long-term interoperability, while maintaining flexibility and applicability across domains. It acknowledges the distinction between planned methods and their execution instances and integrates procedural details with conceptual and contextual elements.

### 4.2 Core Components and High-Level Structure

The ontology is organized around several core high-level classes:

1. **ResearchContext**: Captures metadata about the environment in which the research is conducted
2. **TheoreticalBasis**: Describes the underlying theoretical foundations guiding the research
3. **ResearchProblem**: The core issue or phenomenon addressed by the research
4. **ScientificOpportunity**: Aspects suggesting potential for future progress
5. **ScientificChallenge**: Obstacles related to the research problem, methodology, or implementation
6. **MethodologicalFramework**: The specific structured approach used to address the research problem
7. **MethodExecutionInstance**: Specific implementation of the planned methodology

These high-level classes are related through various properties, creating an interconnected representation of the scientific research process:

- **addresses** (Domain: MethodologicalFramework, Range: ResearchProblem): Links a methodology to the problem it tackles
- **identifies** (Domain: ResearchPublication, Range: ScientificOpportunity/ScientificChallenge): Connects a publication to opportunities or challenges it highlights
- **hasLimitation** (Domain: MethodologicalFramework/ResearchPublication, Range: Limitation): Associates research with its acknowledged limitations
- **hasExecution** (Domain: MethodologicalFramework, Range: MethodExecutionInstance): Links a method plan to its specific executions
- **implementsMethod** (Domain: MethodExecutionInstance, Range: MethodologicalFramework): The inverse of hasExecution
- **arisesFrom** (Domain: ScientificOpportunity, Range: ScientificChallenge/Limitation): Indicates an opportunity that emerges from addressing a challenge
- **motivates** (Domain: ScientificOpportunity, Range: ResearchProblem): Shows how opportunities drive new research problems

### 4.3 Integrated Ontology Table

The following table provides an overview of the key components of the integrated Scientific Knowledge Extraction Ontology:

| Main Branch | Component | Definition | Key Sub-components/Properties |
|------------|------------|------------|----------------------------|
| **Research Context** | ResearchContext | Information situating the research method within its broader scientific and administrative environment | discipline, fieldOfStudy, associatedProject, fundingSource, institution |
| **Theoretical Foundation** | TheoreticalBasis | The underlying theories, established models, specific conceptual frameworks, or philosophical assumptions that inform the research | underlyingTheory, conceptualFramework, guidingModel, philosophicalParadigm, schoolOfThought |
| **Research Problem** | ResearchProblem | The core issue, question, phenomenon, or unsatisfactory situation that the research addresses | problemStatement, problemScope, problemType, problemImportance |
| **Scientific Opportunity** | KnowledgeGap | An identified area where knowledge, understanding, or capability is lacking or insufficient | gapDescription, relatedDomain, gapSignificance |
| **Scientific Opportunity** | ResearchQuestion | A specific, focused, interrogative statement that the research aims to answer | questionText, questionType (exploratory, confirmatory, etc.), relatedVariable |
| **Scientific Opportunity** | FutureDirection | Suggestions for subsequent research steps or areas needing further investigation | directionDescription, timeframe, requiredResources |
| **Scientific Opportunity** | PotentialApplication | A suggested practical use or real-world relevance of the research findings | applicationDescription, targetSector, implementationReadiness |
| **Scientific Challenge** | ScientificChallenge | A fundamental difficulty inherent to the scientific domain or problem complexity | challengeDescription, challengeType, severity |
| **Scientific Challenge** | MethodologicalChallenge | A difficulty related to the design, execution, or analysis phase of the research methodology | challengeDescription, researchPhase, mitigationStrategy |
| **Scientific Challenge** | ImplementationChallenge | A difficulty encountered when applying a method or technology in a concrete setting | challengeDescription, resourceConstraint, technicalHurdle |
| **Scientific Challenge** | Limitation | An acknowledged constraint or shortcoming of the study | limitationDescription, limitationType, impactOnFindings |
| **Methodological Framework** | StudyDesign | Overall strategy or architecture of the inquiry | designType, controlGroup, randomization, blinding, timeDimension |
| **Methodological Framework** | PopulationAndSampling | Description of population and sample selection methods | targetPopulation, sampleSize, samplingMethod, inclusionCriteria |
| **Methodological Framework** | Variables | Measurable characteristics that are controlled, manipulated, or observed | variableName, variableRole, operationalization, measurementScale |
| **Methodological Framework** | MaterialsAndTools | Resources used during execution | itemName, itemType, identifier, specifications, roleInProcedure |
| **Methodological Framework** | Procedure | Step-by-step sequence of actions performed | procedureName, version, hasStep (Step instances) |
| **Methodological Framework** | DataCollection | Specific methods used to gather raw data | collectionMethod, instrumentUsed, collectionSetting |
| **Methodological Framework** | DataAnalysis | Techniques and approaches used to process and analyze data | analysisApproach, statisticalTest, softwareUsed |
| **Methodological Framework** | ResultsRepresentation | Format for presenting outcomes or findings | representationFormat, visualizationType, reportingStandard |
| **Methodological Framework** | ValidationAndVerification | Procedures for ensuring quality and validity | validationType, validationProcedure, validationMetric |
| **Methodological Framework** | EthicalConsiderations | Information regarding ethical oversight and procedures | ethicsApprovalBody, informedConsentProcedure, dataAnonymization |
| **Methodological Framework** | ReproducibilityAndSharing | Information facilitating verification and reuse | dataAvailabilityStatement, codeRepository, protocolAvailability |
| **Method Execution** | MethodExecutionInstance | A specific run or execution of the planned Procedure | executionID, correspondsToPlan, executionDateTime, parameterValuesUsed, deviationsFromPlan, producedData |

## 5. Detailed Component Specification

This section provides detailed definitions, key properties or sub-components, illustrative examples, and guiding questions for each core component of the Scientific Knowledge Extraction Ontology (SKEO).

### 5.1 Research Context Components

#### 5.1.1 ResearchContext

* **Definition:** Information situating the research method within its broader scientific and administrative environment. Helps understand the background and scope of the work.
* **Properties/Sub-components:**
  * discipline (e.g., Controlled Vocabulary: Biology, Physics, Sociology, Computer Science) - Relates to SO:Discipline [22]
  * fieldOfStudy (e.g., String: Molecular Oncology, Particle Physics, Urban Sociology, Machine Learning)
  * associatedProject (e.g., String or URI: Project Name/ID)
  * fundingSource (e.g., String or URI: Funder Name, Grant Number)
  * institution (e.g., String or URI: University, Research Center)
* **Illustrative Examples:**
  * (Biology): Discipline: Biology; Field: Neuroscience; Project: BrainMap Initiative [19]; Funding: NIH Grant X
  * (Computation): Discipline: Computer Science; Field: Ontology Engineering; Project: Wf4Ever [23]; Institution: University of Manchester
* **Guiding Questions:**
  * What is the primary scientific discipline or field of this research?
  * Is this work part of a larger named project or initiative?
  * Which organizations or institutions were involved in conducting the research?
  * Was the research supported by specific funding agencies or grants mentioned in acknowledgements or funding statements?

### 5.2 Theoretical Foundation Components

#### 5.2.1 TheoreticalBasis

* **Definition:** The underlying theories, established models, specific conceptual frameworks, or philosophical assumptions that inform the research question, study design, and interpretation of findings. Explains the 'why' behind the chosen approach.
* **Properties/Sub-components:**
  * underlyingTheory (e.g., String or URI: Theory of Evolution, General Relativity, Social Cognitive Theory). Links to conceptual framework literature [32]
  * conceptualFrameworkReference (e.g., URI or Description: Link to a specific diagram or detailed description of the study's conceptual framework [21])
  * guidingModel (e.g., String or URI: Standard Model of Particle Physics, Climate Model GCM-X, Health Belief Model)
  * philosophicalParadigm (e.g., Controlled Vocabulary: Positivism, Constructivism, Pragmatism, Realism, Relativism). Links to ontological/epistemological discussions [2]
  * schoolOfThought (e.g., String: Bayesian statistics, Grounded theory). Links to SO:SchoolOfThought [22]
* **Illustrative Examples:**
  * (Psychology): Underlying Theory: Theory of Planned Behavior; Philosophical Paradigm: Positivism
  * (Physics): Guiding Model: Standard Model; School of Thought: Frequentist statistics
  * (Education): Conceptual Framework: Described in Figure 1 [33]; Philosophical Paradigm: Constructivism
* **Guiding Questions:**
  * Does the paper reference any specific theories or theoretical frameworks that motivate the study or guide the analysis? (Check Introduction, Literature Review, Discussion)
  * Is a conceptual framework explicitly presented (textually or visually)? [21]
  * Are there references to specific established models being tested or applied?
  * Does the methodology section imply adherence to a particular philosophical approach (e.g., quantitative/realist vs. qualitative/relativist)? [2]
  * Does the paper mention a specific school of thought influencing the methods (e.g., Bayesian methods, grounded theory approach)?

### 5.3 Research Problem Components

#### 5.3.1 ResearchProblem (RP)

* **Definition:** The core issue, question, phenomenon, or unsatisfactory situation that the research fundamentally aims to address, understand, explain, or solve. It represents the central challenge motivating the entire study and provides the context for the methods, results, and conclusions [1]. While it frames the research, it is itself the primary challenge being tackled.
* **Properties/Sub-components:**
  * problemStatement (String: Concise description of the problem)
  * problemScope (String: Boundaries of the problem being addressed)
  * problemType (e.g., Controlled Vocabulary: Knowledge Problem, Design Problem, Empirical Problem)
  * problemImportance (String: Significance or impact of solving the problem)
  * businessRelevance (String: Description of how the problem relates to business needs, market gaps, or industry challenges; potential economic impact of solving the problem)
* **Illustrative Examples:**
  * (Medicine): "Developing an effective vaccine against HIV." [25]
  * (Computer Science): "Ontology learning from text." [7] or "Designing epidemiological surveillance systems." [7] or "Rapid detection of microorganisms." [26]
  * (Environmental Science): "Assessing the effects of environmental governance systems on conservation outcomes." [33]
  * (Physics): "Achieving practical quantum key distribution." [25]
  * (Information Systems): "How to systematically assess the importance of research problems." [21]
  * (Industry Research): "Reducing manufacturing defects in semiconductor production." businessRelevance: "Could lower production costs by 15% and increase yield rates for high-demand consumer electronics components."
  * (Applied AI): "Developing more efficient natural language processing algorithms." businessRelevance: "Enables more cost-effective customer service automation and multilingual market expansion for global businesses."
* **Guiding Questions:**
  * What is the main, overarching issue, problem, or question that the paper states it seeks to tackle or investigate?
  * What fundamental phenomenon or unsatisfactory situation is being studied or addressed?
  * What is presented in the introduction as the primary motivation, context, or justification for conducting the research?
  * What core challenge does the entire paper revolve around solving or understanding?
  * "Does the paper mention how solving this research problem might benefit specific industries or business processes?"
  * "Is there discussion of potential cost savings, efficiency improvements, or new market opportunities that could result from addressing this problem?"

### 5.4 Scientific Opportunity Components

#### 5.4.1 KnowledgeGap

* **Definition:** An identified area within a specific field where knowledge, understanding, data, or capability is recognized as lacking, insufficient, or uncertain based on the current state of the art. Identifying a knowledge gap often serves as a primary motivation for undertaking the ResearchProblem [27]. It represents a deficit that the research aims to fill.
* **Properties/Sub-components:**
  * gapDescription (String: Description of the specific lack of knowledge or capability)
  * relatedDomain (String: The field or area where the gap exists)
  * gapSignificance (String: Why filling this gap is important)
* **Illustrative Examples:**
  * (Medicine): "Current understanding of the long-term neurological effects of COVID-19 infection is limited." (Implicit gap: need for long-term studies)
  * (Computer Science): "There is a lack of robust benchmarks for evaluating the fairness of graph embedding algorithms." [33] (Explicit gap)
  * (Environmental Science): "The cumulative impact of different types of agricultural runoff on coastal water quality remains poorly quantified." [27] (Implicit gap: need for comprehensive measurement/modeling)
  * (Materials Science): "Fundamental understanding of interfacial phenomena in solid-state batteries is incomplete, hindering performance improvements."
* **Guiding Questions:**
  * What does the paper state is unknown, missing, poorly understood, or lacking in the current literature or state-of-the-art?
  * Does the introduction or background section explicitly highlight a lack of knowledge, data, tools, or capability as a motivation for the study?
  * What specific deficiency in existing knowledge or methods does this research explicitly aim to address or fill?
  * Are phrases like 'limited understanding', 'poorly understood', 'lack of data', 'knowledge gap', 'remains unclear' used to describe the state of the field?

#### 5.4.2 ResearchQuestion (RQ)

* **Definition:** A specific, focused, interrogative statement that the research aims to answer directly. It serves to operationalize the investigation of a broader ResearchProblem or KnowledgeGap, providing clear direction for the study's methodology and analysis [13]. RQs make the general problem concrete and testable.
* **Properties/Sub-components:**
  * questionText (String: The actual question being asked)
  * questionType (e.g., Controlled Vocabulary: Descriptive, Explanatory, Predictive, Evaluative)
  * relatedVariable (Link to specific Variables investigated in the question)
* **Illustrative Examples:**
  * (Particle Physics): "What is the precise mass of the W boson?"
  * (Neuroscience): "How does optogenetic stimulation of dopamine neurons in the VTA affect reward-seeking behavior in rats?"
  * (Information Systems): "Is it possible to organise the information of an emerging domain by using an ontology approach?" [16]
  * (Political Science): "Does increased foreign aid correlate with decreased levels of government corruption in developing nations?"
* **Guiding Questions:**
  * "What specific question(s) does this paper explicitly state it is trying to answer?"
  * "Is there a sentence phrased as a question (often ending with '?') that outlines the core investigation, typically found in the introduction or abstract?"
  * "What query guides the specific methodology, data collection, and analysis presented in the paper?"
  * "Does the paper frame its objective in the form of a direct question to be addressed?"

#### 5.4.3 FutureDirection

* **Definition:** Explicit suggestions, recommendations, or proposals made by the authors for subsequent research activities that should follow from the current work. These often arise from the study's findings, limitations, or unanswered questions, pointing towards specific next steps or promising avenues for further investigation [19].
* **Properties/Sub-components:**
  * directionDescription (String: Description of the suggested research direction)
  * timeframe (String: Short-term, medium-term, or long-term suggestion)
  * requiredResources (String: Resources needed to pursue this direction)
* **Illustrative Examples:**
  * (Chemistry): "Future work will focus on scaling up the synthesis process and testing catalytic activity under industrial conditions." [35]
  * (Psychology): "Further research is needed to explore the moderating role of personality traits in the observed effects." [38]
  * (Computer Science): "An interesting direction for future work is to investigate the applicability of this algorithm to dynamic graphs." [25]
  * (Biology): "Exploring the downstream targets of this transcription factor represents a key area for future investigation." [36]
  * (Ontology Engineering): "Future work includes implementing an interactive KB system to evaluate in DSR projects and experimental development of intelligent agents." [38]
* **Guiding Questions:**
  * "Does the paper explicitly suggest specific next steps, follow-up studies, or new research questions in the conclusion, discussion, or a dedicated 'Future Work' section?"
  * "Are there phrases like 'future work should...', 'further research is needed...', 'a promising direction is...', 'it would be interesting to explore...', 'next steps include...'?"
  * "What unresolved questions, potential extensions, or new avenues for investigation does the paper explicitly point towards based on its own results or limitations?"

#### 5.4.4 PotentialApplication

* **Definition:** A suggested or envisioned practical use, implication, benefit, or real-world relevance of the research findings, methods, developed artifacts (e.g., models, algorithms, materials), or acquired knowledge. This extends beyond the immediate academic contribution to potential impact in industry, policy, clinical practice, or society [32].
* **Properties/Sub-components:**
  * applicationDescription (String: Description of the potential application)
  * targetSector (String: Industry, healthcare, education, etc. where application is relevant)
  * implementationReadiness (e.g., Controlled Vocabulary: Conceptual, Prototype, Ready for Deployment)
* **Illustrative Examples:**
  * (Materials Science): "The enhanced durability of this concrete formulation suggests potential applications in infrastructure projects in harsh environments."
  * (Artificial Intelligence): "The developed natural language processing model could be applied to improve automated customer service systems." [32]
  * (Biotechnology): "This gene editing technique holds potential for therapeutic applications in treating genetic disorders."
  * (Education): "The findings on student motivation could inform the design of more effective online learning platforms."
  * (Ontology Learning): "Automatically learned ontologies show potential for improving classification and clustering tasks and debugging ontology mappings." [32]
* **Guiding Questions:**
  * "Does the paper suggest how the findings, methods, or developed technology could be used in practice or outside of a purely academic setting?"
  * "Are potential real-world uses, practical implications, or broader societal relevance mentioned, often in the introduction or conclusion?"
  * "Does the paper discuss the potential impact or utility of the work for specific industries, applications, or societal problems?"
  * "Are phrases like 'potential applications include...', 'could be used for...', 'has implications for...', 'relevant to...' used in reference to practical outcomes?"

#### 5.5.1 ScientificChallenge

* **Definition:** A fundamental difficulty or obstacle inherent to the scientific domain itself, the nature of the phenomenon under investigation, or the current limits of scientific theory or understanding. These challenges often relate to intrinsic complexity, scale, randomness, emergent behavior, or the lack of foundational theories or models. They are distinct from difficulties arising from specific methods or implementations [23].
* **Properties/Sub-components:**
  * challengeDescription (String: Description of the fundamental challenge)
  * challengeType (e.g., Controlled Vocabulary: Complexity Challenge, Scale Challenge, Theory Gap)
  * severity (e.g., Controlled Vocabulary: Minor, Moderate, Major, Fundamental)
* **Illustrative Examples:**
  * (Physics): "The challenge of unifying quantum mechanics and general relativity into a single theoretical framework." [24]
  * (Biology): "Understanding the complex interplay of genetic and environmental factors in multifactorial diseases poses a significant scientific challenge." [24]
  * (Environmental Management): "Predicting chemical reactivity and solvent structure at interfaces far from equilibrium in complex waste mixtures." [27]
  * (Neuroscience): "The inherent complexity and interconnectedness of the human brain makes mapping neural circuits a major scientific challenge."
  * (Paralympic Sport): "Development and reporting of valid measures of impairment is currently the most pressing scientific challenge in evidence-based classification." [23]
* **Guiding Questions:**
  * "Does the paper mention fundamental difficulties related to the underlying science, the nature of the system being studied, or the limits of current theory?"
  * "Are challenges related to inherent complexity, scale, randomness, emergence, or a lack of basic scientific understanding discussed?"
  * "What obstacles, described as fundamental or scientific, make this research problem inherently difficult to solve, irrespective of the specific method chosen?"
  * "Are phrases like 'fundamental challenge', 'scientific challenge', 'inherent complexity', 'lack of foundational understanding' used?"

#### 5.5.2 MethodologicalChallenge

* **Definition:** A difficulty, hurdle, complexity, or potential source of error encountered or inherent in the specific research methodology employed. This includes issues related to study design, data collection procedures, measurement validity and reliability, sampling strategies, experimental control, potential biases (e.g., common source bias [39]), ethical considerations in execution, or the application of analytical techniques [14].
* **Properties/Sub-components:**
  * challengeDescription (String: Description of the methodological challenge)
  * researchPhase (e.g., Controlled Vocabulary: Study Design, Data Collection, Analysis, Interpretation)
  * mitigationStrategy (String: Approaches used to address or minimize the challenge)
* **Illustrative Examples:**
  * (Social Science): "Engaging 'hard-to-reach' groups in research presents significant methodological difficulties in recruitment and ensuring authentic participation." [30]
  * (Psychology): "Controlling for experimenter demand characteristics was a methodological challenge in this study." [29]
  * (Ecology): "Obtaining accurate and unbiased samples of elusive species in large, heterogeneous habitats poses methodological challenges."
  * (Media Studies): "Collecting reliable data on informal media education initiatives is methodologically challenging due to lack of available information." [31]
  * (Evaluation Research): "Defining and measuring the 'value' of cultural interventions presents considerable methodological difficulties for evaluators." [28]
* **Guiding Questions:**
  * "Does the paper describe difficulties specifically related to the study design, data collection process, measurement tools, sampling methods, or data analysis techniques used?"
  * "Are issues like bias (sampling bias, measurement bias, common method bias), confounding variables, lack of control, ethical hurdles in data collection, or problems with statistical analysis mentioned?"
  * "What obstacles arose specifically from *how* the research was planned, conducted, or analyzed?"
  * "Are phrases like 'methodological challenge', 'methodological difficulty', 'data collection issues', 'measurement problems', 'sampling limitations', 'potential bias' used?"

#### 5.5.3 ImplementationChallenge

* **Definition:** A specific difficulty, obstacle, or constraint encountered when attempting to build, deploy, apply, or scale a particular approach, method, algorithm, technology, or intervention in a concrete or real-world setting. These challenges are often related to technical hurdles, system integration, resource limitations (cost, time, hardware, infrastructure), scalability, usability, or dealing with the complexities of practical application environments.
* **Properties/Sub-components:**
  * challengeDescription (String: Description of the implementation challenge)
  * resourceConstraint (e.g., String: Cost, Time, Hardware, Personnel, etc.)
  * technicalHurdle (String: Specific technical difficulty encountered)
* **Illustrative Examples:**
  * (Quantum Computing): "Practical challenges in quantum key distribution include achieving high secret key rates over long distances with cost-effective and compact hardware." [25]
  * (Software Engineering): "Integrating the new machine learning module with the existing legacy codebase presented significant implementation challenges."
  * (Robotics): "Deploying autonomous robots in dynamic, unpredictable human environments faces practical challenges related to safety and reliability."
  * (Medical Devices): "Miniaturizing the sensor technology for integration into a wearable device encountered practical challenges related to power consumption and manufacturing."
  * (Ontology Engineering): "Turning the results of an ontology learning algorithm into an ontology that reflects a desired conceptualization can be costly and challenging." [32]
* **Guiding Questions:**
  * "Does the paper describe problems encountered when building, deploying, testing, scaling, or applying the proposed method, algorithm, system, or technology?"
  * "Are technical difficulties, resource limitations (cost, time, hardware, data availability for training), scalability issues, integration problems, or hurdles related to real-world deployment discussed?"
  * "What obstacles were specific to the *realization*, *application*, or *operationalization* of the proposed approach or technology?"
  * "Are phrases like 'implementation challenge', 'practical difficulty', 'technical hurdle', 'scalability issue', 'resource constraints', 'deployment problems' used?"

#### 5.5.4 Limitation

* **Definition:** An acknowledged constraint, shortcoming, boundary, or weakness of the study's scope, methodology, data, analysis, or findings, as stated by the authors. Limitations potentially affect the interpretation, validity, generalizability, or applicability of the research results. They represent the recognized boundaries of the contribution, distinct from challenges encountered during the research process.
* **Properties/Sub-components:**
  * limitationDescription (String: Description of the specific limitation)
  * limitationType (e.g., Controlled Vocabulary: Sample Size Limitation, Generalizability Issue, Measurement Error, Selection Bias, Scope Limitation)
  * impactOnFindings (String: How the limitation might affect results or conclusions)
  * businessConstraints (String: How the limitation might affect practical implementation in business settings, including cost barriers, scalability issues, implementation timeframes, or regulatory hurdles)
* **Illustrative Examples:**
  * (Study Design): "A limitation of this study is its reliance on a correlational design, which prevents definitive causal conclusions." [29]
  * (Sample): "The findings are based on a small, geographically limited sample, which may limit generalizability to other populations."
  * (Method): "The use of self-report questionnaires is a limitation, as it may be subject to recall bias." [39]
  * (Scope): "This economic model does not incorporate environmental externalities, which is a limitation of the analysis." [20]
  * (Data): "The analysis was limited by the availability of public data, potentially missing key variables." [33]
  * (Ontology): "Learned ontologies may suffer from limitations such as lack of coverage or noise." [32]
  * (AI Implementation): Limitation Description: "Model was trained on high-end specialized hardware"; businessConstraints: "Deployment requires substantial computing infrastructure investment, making adoption economically feasible only for large enterprises."
  * (Manufacturing Process): Limitation Description: "Process tested only at laboratory scale"; businessConstraints: "Industrial scale-up would require significant capital expenditure and regulatory approval, with an estimated 2-3 year timeline before commercial viability."
* **Guiding Questions:**
  * "What constraints, shortcomings, weaknesses, or boundaries does the paper explicitly acknowledge about its own approach, data, analysis, or findings (often found in a 'Discussion' or dedicated 'Limitations' section)?"
  * "Are limitations regarding the study's scope, generalizability, validity, reliability, methodology, or data explicitly stated by the authors?"
  * "What caveats or qualifications do the authors themselves place on their conclusions or the applicability of their work?"
  * "Are phrases like 'a limitation of this study is...', 'findings may not generalize because...', 'the scope was limited to...', 'we acknowledge that...', 'a shortcoming is...' used?"
  * "Does the paper discuss how limitations might impact the commercial viability or business application of the findings?"
  * "Are there acknowledged constraints related to cost, infrastructure requirements, or regulatory compliance that would affect business adoption?"

### 5.6 Methodological Framework Components

#### 5.6.1 StudyDesign

* **Definition:** The overall plan or strategy chosen to integrate the different components of the research project logically and coherently, enabling the effective addressing of the research objective. Defines the architectural blueprint of the inquiry.
* **Properties/Sub-components:**
  * designType (e.g., Controlled Vocabulary: Experimental, Quasi-Experimental, Randomized Controlled Trial (RCT), Observational, Cohort Study, Case-Control Study, Cross-Sectional Study, Longitudinal Study, Survey, Case Study, Ethnography, Grounded Theory, Simulation, Meta-Analysis). Links to EXPO experiment types [8]
  * controlGroup (Boolean: Does the design include a control group?)
  * randomization (Boolean: Was randomization used for group assignment?)
  * blinding (e.g., Controlled Vocabulary: None, Single-Blind, Double-Blind)
  * timeDimension (e.g., Controlled Vocabulary: Cross-Sectional, Longitudinal, Retrospective, Prospective)
* **Illustrative Examples:**
  * (Medicine): Design Type: Randomized Controlled Trial; Control Group: True; Randomization: True; Blinding: Double-Blind; Time Dimension: Prospective
  * (Sociology): Design Type: Cross-Sectional Survey; Control Group: False; Randomization: False (or N/A); Time Dimension: Cross-Sectional
  * (Ecology): Design Type: Observational Cohort Study; Time Dimension: Longitudinal
  * (Computation): Design Type: Simulation
* **Guiding Questions:**
  * "What overall research design is employed (e.g., experiment, survey, case study, simulation)? (Often stated in Methods)"
  * "Does the study involve manipulating variables and comparing groups (experimental)?" [2]
  * "Is there a control or comparison group?"
  * "Were participants or units randomly assigned to groups?"
  * "Were participants or researchers blinded to group assignments or interventions?"
  * "Does the study collect data at a single point in time (cross-sectional) or over a period (longitudinal)?"

#### 5.6.2 PopulationAndSampling

* **Definition:** Description of the broader group to which the study's findings are intended to apply (population) and the specific subset of this group from which data were collected (sample), including the methods used to select the sample.
* **Properties/Sub-components:**
  * targetPopulation (String: Description of the population of interest)
  * samplingFrame (String: The list or map from which the sample was drawn, if applicable)
  * sampleSize (Integer: Number of participants or units in the final sample)
  * samplingMethod (e.g., Controlled Vocabulary: Probability Sampling, Non-Probability Sampling)
  * inclusionCriteria (String: Characteristics required for participants/units to be included)
  * exclusionCriteria (String: Characteristics that disqualify participants/units)
  * responseRate (Percentage, if applicable, e.g., for surveys)
* **Illustrative Examples:**
  * (Survey): Target Population: Undergraduate students at University Z; Sample Size: 500; Sampling Method: Stratified random sampling based on year of study; Inclusion Criteria: Currently enrolled full-time
  * (Experiment): Target Population: Adults with Type 2 Diabetes; Sample Size: 60; Sampling Method: Convenience sampling from Clinic Y; Exclusion Criteria: Co-morbidities A, B, C
  * (Qualitative): Target Population: High school teachers in District X; Sample Size: 15; Sampling Method: Purposive sampling (seeking diverse experience levels)
* **Guiding Questions:**
  * "Who or what was studied (participants, specimens, datasets, etc.)?"
  * "What is the broader group the researchers aim to generalize their findings to?"
  * "How many participants or units were included in the final analysis?"
  * "How were the participants or units selected for the study? Was it random or non-random?"
  * "What were the specific criteria for including or excluding participants/units?"
  * "What was the response rate or participation rate, if applicable?"

#### 5.6.3 Variables

* **Definition:** Measurable characteristics, conditions, attributes, or factors that are controlled, manipulated, or observed in a study. These are the core elements whose relationships are typically investigated. Central to conceptual frameworks [21] and experimental design [8].
* **Properties/Sub-components (for each variable):**
  * variableName (String: e.g., "Blood Pressure", "Treatment Group", "Age", "Gene Expression Level")
  * variableRole (Controlled Vocabulary: Independent, Dependent, Mediator, Moderator, Control, Confounder, Covariate, Outcome). Links to conceptual framework variable types [21]
  * conceptualDefinition (String: Theoretical definition of the variable)
  * operationalization (String: How the variable was measured or manipulated in practice)
  * measurementScale (Controlled Vocabulary: Nominal, Ordinal, Interval, Ratio, Categorical, Continuous)
  * units (String: Unit of measurement, e.g., "mmHg", "Years", "Fold Change", "Likert Scale Score")
* **Illustrative Examples:**
  * (Variable 1): Name: "Drug Dosage"; Role: Independent; Operationalization: "Oral administration of 10mg or 20mg"; Scale: Nominal/Ordinal; Units: "mg"
  * (Variable 2): Name: "Systolic Blood Pressure"; Role: Dependent; Operationalization: "Measured using sphygmomanometer model Z after 5 min rest"; Scale: Ratio; Units: "mmHg"
  * (Variable 3): Name: "IQ Score"; Role: Moderator; Operationalization: "Score on WAIS-IV test"; Scale: Interval; Units: "Points"
  * (Variable 4): Name: "Room Temperature"; Role: Control; Operationalization: "Maintained via thermostat setting"; Scale: Interval; Units: "°C"
* **Guiding Questions:**
  * "What are the key factors being manipulated or compared by the researchers (independent variables)?" [32]
  * "What are the main outcomes or results being measured (dependent variables)?" [32]
  * "How was each key variable defined and measured or manipulated in this specific study (operationalization)?"
  * "Are any variables identified as potentially influencing the main relationship (moderators) or explaining it (mediators)?" [32]
  * "What factors were held constant or statistically adjusted for (control variables, covariates)?" [32]
  * "What are the units of measurement for quantitative variables?"

#### 5.6.4 MaterialsAndTools

* **Definition:** Resources, including physical objects, software, datasets, or conceptual instruments (like questionnaires), that are utilized during the execution of the procedure but are not the primary object of study themselves (unless the study is methodological).
* **Properties/Sub-components (for each item):**
  * itemName (String: e.g., "Spectrophotometer Model X", "SPSS v28", "fMRI Scanner 3T", "Gene Ontology Database", "Beck Depression Inventory")
  * itemType (Controlled Vocabulary: Equipment, Software, Dataset, Reagent, Biological Sample Type, Questionnaire, Ontology, Database, Protocol). Links to SO:Tool [22], EXPO:Equipment [8], RO:Resource [23]
  * identifier (String or URI: e.g., Manufacturer, Version Number, DOI, Accession Number, URL)
  * specifications (String: Key technical details, e.g., "Resolution 1nm", "Python 3.9", "Release 2023_01")
  * roleInProcedure (String: Brief description of how the item was used)
* **Illustrative Examples (continued):**
  * (Survey): Item Name: "SF-36 Health Survey"; Item Type: Questionnaire; Identifier: "Standard version"; Role: "Used to measure health-related quality of life"
  * (Bioinformatics): Item Name: "UniProtKB"; Item Type: Database; Identifier: "Release 2024_03"; Role: "Used for protein sequence annotation"
* **Guiding Questions:**
  * "What specific equipment, instruments, or apparatus were used? Are model numbers or manufacturers provided?"
  * "What software packages (including versions) were used for data collection, processing, analysis, or simulation?"
  * "Were specific biological reagents, cell lines, or chemical compounds used? Are sources or catalog numbers provided?"
  * "Were standardized questionnaires, tests, or scales employed?"
  * "Were specific datasets, databases, or ontologies used as input or reference? Are identifiers or versions given?"

#### 5.6.5 Procedure

* **Definition:** The detailed, ordered sequence of steps or actions undertaken to execute the study design and collect data. Represents the core workflow, protocol, or experimental method. Must distinguish the planned procedure (template/design) from actual execution instances.
* **Properties/Structure:** Requires a structured representation (e.g., list of Steps).
  * **For the overall Procedure (Plan/Template):**
    * procedureName (String: e.g., "Protein Extraction Protocol", "Survey Administration Workflow", "Finite Element Simulation Steps")
    * version (String, optional)
    * hasStep (Ordered list of Step instances). Links to SO:Method/hasPart [22], RO:wfdesc:hasSubProcess [24], EXPO:ExperimentalActions [8]
  * **For each Step:**
    * stepNumber (Integer: Sequence order)
    * description (String: Detailed description of the action)
    * inputs (Links to MaterialsAndTools or outputs of previous steps)
    * outputs (Description of data or material generated)
    * toolUsed (Link to MaterialsAndTools)
    * parameters (List of key-value pairs for settings, e.g., {"temperature": "60°C", "duration": "30min"})
    * subSteps (Optional nested list of Step instances for complex actions)
    * controlFlow (Optional: e.g., Conditional [if/then], Loop, Parallel). Links to workflow concepts
* **Illustrative Examples:**
  * (Chemistry Protocol): Procedure Name: "Synthesis Method A"; Step 1: {Number: 1, Description: "Dissolve 5g compound A in 100ml solvent B", Inputs:, Outputs: "Solution 1"}; Step 2: {Number: 2, Description: "Heat Solution 1", ToolUsed: "Heater Model Y", Parameters: {"temperature": "60°C", "duration": "30min"}, Inputs:, Outputs: "Heated Solution 1"};...
  * (Computational Workflow): Procedure Name: "Gene Prioritization Workflow" [23]; hasStep:...
* **Guiding Questions:**
  * "Can you outline the sequence of major steps performed in the study/experiment/analysis?"
  * "What specific actions were taken at each stage?"
  * "Are specific protocols, standard operating procedures (SOPs), or workflow diagrams referenced or described in detail?" [23]
  * "What were the inputs and outputs of each major step?"
  * "What key parameters or settings were used for each step or associated tool (e.g., time, temperature, concentration, software settings)?"

#### 5.6.6 DataCollection

* **Definition:** Specific methods, techniques, and instruments used within the Procedure to actively gather or generate the raw data for the study. Focuses on the measurement or observation act itself.
* **Properties/Sub-components:**
  * collectionMethod (e.g., Controlled Vocabulary: Survey Administration, Interview, Observation, Sensor Reading, Image Acquisition, Physiological Measurement, Document Analysis, Log File Extraction)
  * instrumentUsed (Link to specific MaterialsAndTools instance used for collection, e.g., questionnaire, recorder, microscope, sensor)
  * collectionSetting (String: e.g., "Laboratory", "Online Platform", "Field Site", "Clinic")
  * collectionTimeframe (String or Date Range: e.g., "March-April 2023", "During task performance")
  * dataRecordingFormat (String: e.g., "Digital audio file", "CSV spreadsheet", "DICOM image", "Handwritten notes")
* **Illustrative Examples:**
  * (Survey): Collection Method: Survey Administration; Instrument Used: SF-36 Questionnaire [link]; Collection Setting: Online Platform Qualtrics; Data Recording Format: CSV
  * (Neuroimaging): Collection Method: Image Acquisition; Instrument Used: fMRI Scanner 3T [link]; Collection Setting: Hospital Imaging Center; Data Recording Format: DICOM
  * (Qualitative): Collection Method: Interview; Instrument Used: Semi-structured interview guide [link]; Collection Setting: Participant's workplace; Data Recording Format: Digital audio recording, Transcripts
* **Guiding Questions:**
  * "How was the raw data actually gathered or generated?"
  * "What specific tools or instruments were used for measurement or observation?"
  * "Where and when did data collection take place?"
  * "In what format was the raw data initially recorded?"

#### 5.6.7 DataAnalysis

* **Definition:** Techniques, algorithms, statistical procedures, qualitative methods, and software tools applied to the collected data to process, summarize, model, interpret, and derive findings.
* **Properties/Sub-components:**
  * analysisApproach (e.g., Controlled Vocabulary: Statistical Analysis, Machine Learning, Qualitative Content Analysis, Thematic Analysis, Simulation Analysis, Mathematical Modeling)
  * statisticalTest (e.g., String or Controlled Vocabulary: t-test, ANOVA, Regression Analysis, Chi-squared Test, Correlation Analysis)
  * algorithmUsed (e.g., String or URI: Support Vector Machine, K-means Clustering, BLAST alignment)
  * qualitativeCodingScheme (String or URI: Description or link to the coding framework used)
  * softwareUsed (Link to specific MaterialsAndTools instance, e.g., R, Python [with libraries], SPSS, NVivo, MATLAB)
  * parameterSettings (String: Key parameters for algorithms or models, e.g., "p-value threshold=0.05", "Cross-validation folds=10")
  * dataPreprocessingSteps (String: Description of cleaning, transformation, normalization steps)
* **Illustrative Examples:**
  * (Quantitative): Analysis Approach: Statistical Analysis; Statistical Test: Two-way ANOVA; Software Used: SPSS v28 [link]; Parameter Settings: "Significance level alpha=0.05"
  * (Machine Learning): Analysis Approach: Machine Learning; Algorithm Used: Random Forest Classifier; Software Used: Python scikit-learn library [link]; Parameter Settings: "n_estimators=100"
  * (Qualitative): Analysis Approach: Thematic Analysis; Qualitative Coding Scheme: Braun & Clarke's 6 phases [link]; Software Used: NVivo 12 [link]
* **Guiding Questions:**
  * "How was the collected data processed or cleaned before analysis?"
  * "What specific statistical tests, algorithms, or analytical techniques were applied?"
  * "What software (including version and relevant packages/libraries) was used for the analysis?"
  * "Were specific parameters or thresholds used in the analysis (e.g., significance levels, model hyperparameters)?"
  * "If qualitative data was analyzed, what coding or analytical approach was used?"

#### 5.6.8 ResultsRepresentation

* **Definition:** The format and manner in which the outcomes or findings derived from the DataAnalysis are presented or summarized.
* **Properties/Sub-components:**
  * representationFormat (e.g., Controlled Vocabulary: Tabular Data, Statistical Summary (Mean, SD, p-value), Graph/Plot, Image, Textual Description, Mathematical Equation, Model Output File)
  * visualizationType (e.g., String: Bar chart, Scatter plot, Heatmap, Network diagram, if applicable)
  * reportingStandard (e.g., String or URI: CONSORT, PRISMA, MIAME, if applicable)
  * primaryOutcomeMeasure (Link to the specific Variable designated as primary outcome)
* **Illustrative Examples:**
  * (Experiment): Representation Format: Tabular Data (Table 1), Graph/Plot (Figure 2); Visualization Type: Bar chart with error bars; Primary Outcome Measure: "Tumor Volume" [link]
  * (Meta-Analysis): Representation Format: Forest Plot; Reporting Standard: PRISMA
  * (Qualitative): Representation Format: Textual Description (Themes), Quotations
* **Guiding Questions:**
  * "How are the main findings presented in the paper (e.g., tables, figures, text)?"
  * "What types of graphs or visualizations are used to show results?"
  * "Are specific reporting guidelines or standards mentioned (e.g., CONSORT for trials)?"
  * "What specific metrics or summaries are reported (e.g., means, p-values, effect sizes, qualitative themes)?"

#### 5.6.9 ValidationAndVerification

* **Definition:** Procedures and criteria used to assess and ensure the accuracy, reliability, robustness, and validity of the methodology, instruments, data, or results. Includes quality control measures.
* **Properties/Sub-components:**
  * validationType (e.g., Controlled Vocabulary: Instrument Calibration, Internal Validity Check, External Validity Check, Statistical Validation (e.g., cross-validation), Replicate Analysis, Control Experiment, Sensitivity Analysis, Inter-rater Reliability Check, Fault Tolerance Check). Links to fault handling [25]
  * validationProcedure (String: Description of the validation steps performed)
  * validationMetric (String: e.g., "Correlation coefficient", "Kappa statistic", "RMSE", "Accuracy")
  * validationResult (String: Outcome of the validation, e.g., "Calibration successful within ±1%", "Inter-rater reliability Kappa=0.85")
  * industryStandards (String or URI: Relevant industry standards, certifications, or regulatory frameworks that the method complies with or was validated against)
* **Illustrative Examples:**
  * (Measurement): Validation Type: Instrument Calibration; Procedure: "Calibrated against standard X monthly"; Result: "Deviation < 0.5%"
  * (Survey): Validation Type: Internal Validity Check; Procedure: "Factor analysis performed on scale items"; Result: "Confirmed expected factor structure"
  * (Machine Learning): Validation Type: Statistical Validation; Procedure: "10-fold cross-validation"; Metric: "Area Under Curve (AUC)"; Result: "Mean AUC = 0.92"
  * (Qualitative): Validation Type: Inter-rater Reliability Check; Procedure: "Two coders independently coded 20% of transcripts"; Metric: "Cohen's Kappa"; Result: "Kappa = 0.88"
  * (Medical Device): Validation Type: Performance Testing; industryStandards: "Validated according to ISO 13485:2016 for medical device quality management systems and IEC 62304 for medical device software."
  * (Chemical Analysis): Validation Type: Method Validation; industryStandards: "Procedure follows ASTM D1193 standards for reagent water and FDA Guidance for Industry: Analytical Procedures and Methods Validation for Drugs and Biologics."
* **Guiding Questions:**
  * "What steps were taken to ensure the measurement instruments were accurate (calibration, validation)?"
  * "Were control experiments performed?"
  * "How was the reliability or validity of scales, questionnaires, or coding schemes assessed?"
  * "Were statistical validation techniques like cross-validation used?"
  * "Were sensitivity analyses conducted to test robustness to assumptions or parameters?"
  * "How were potential errors or faults in workflows or procedures handled or checked?" [25]
  * "Does the validation process reference compliance with specific industry standards or regulatory requirements?"
  * "Were quality control measures aligned with established industry best practices or certification frameworks?"

#### 5.6.10 EthicalConsiderations

* **Definition:** Information regarding the ethical oversight and procedures followed during the research, particularly concerning human participants, animal subjects, or sensitive data.
* **Properties/Sub-components:**
  * ethicsApprovalBody (String: e.g., "Institutional Review Board (IRB) of University X", "Animal Care and Use Committee Y")
  * approvalIdentifier (String: Protocol or approval number)
  * informedConsentProcedure (String: Description of how consent was obtained, e.g., "Written informed consent obtained from all participants")
  * animalWelfareCompliance (String: Reference to guidelines followed, e.g., "ARRIVE guidelines")
  * dataAnonymization (Boolean: Was data anonymized or de-identified?)
  * privacyMeasures (String: Description of steps taken to protect participant privacy)
* **Illustrative Examples:**
  * (Human Study): Approval Body: "University IRB"; Approval ID: "Protocol #12345"; Consent: "Written informed consent"; Anonymization: True
  * (Animal Study): Approval Body: "IACUC Committee Z"; Compliance: "Followed institutional guidelines based on the Guide for the Care and Use of Laboratory Animals"
* **Guiding Questions:**
  * "Was ethical approval obtained for the study? From which committee or board?"
  * "Is an approval number or protocol identifier provided?"
  * "How was informed consent obtained from human participants?"
  * "Were specific guidelines for animal welfare followed?"
  * "What measures were taken to protect participant confidentiality or anonymize data?"

#### 5.6.11 ReproducibilityAndSharing

* **Definition:** Information facilitating the verification, replication, and reuse of the research method and findings by others. Includes details on the availability of essential research components.
* **Properties/Sub-components:**
  * dataAvailabilityStatement (String: Text describing where and how data can be accessed). Links strongly to RO principles [3]
  * dataRepository (String or URI: Name and link to repository, e.g., "GenBank", "Dryad", "Zenodo")
  * dataAccessionNumber (String: Identifier for the specific dataset)
  * codeAvailabilityStatement (String: Text describing code availability)
  * codeRepository (String or URI: e.g., "GitHub", "Bitbucket")
  * protocolAvailability (String or URI: Link to detailed protocol, e.g., "protocols.io", "Supplementary Information")
  * materialsAvailability (String: Information on obtaining unique reagents or materials)
  * softwareEnvironment (String: Details on OS, libraries, dependencies needed to run code). Links to RO concepts [27]
  * commercializationPartners (String or URI: Organizations involved in translating the research into commercial applications, licensing agreements, or industry collaborations for practical implementation)
* **Illustrative Examples:**
  * (Genomics): Data Statement: "Raw sequencing data are available at NCBI SRA"; Repository: "NCBI SRA"; Accession: "PRJNAxxxxxx"
  * (Computation): Code Statement: "Analysis code available on GitHub"; Repository: "github.com/user/repo"; Environment: "Python 3.8, requirements.txt provided"
  * (Experiment): Protocol Statement: "Detailed protocol available in Supplementary Methods and on protocols.io"; URI: "dx.doi.org/10.17504/protocols.io.xxxx"
  * (Biotechnology): Protocol Statement: "Detailed protocol available in Supplementary Methods"; commercializationPartners: "Method licensed to BioTech Inc. for commercial kit development, contact licensing@biotech.com for commercial use."
  * (Software): Code Statement: "Core algorithm available on GitHub under academic license"; commercializationPartners: "Commercial applications being developed with CloudSoft Solutions; see www.cloudsoftpartners.com/researchers"
* **Guiding Questions:**
  * "Is there a statement about the availability of the data used or generated? Where can it be found?"
  * "Is an accession number or persistent identifier provided for the data?"
  * "Is the analysis code or software made available? Where?"
  * "Is a detailed protocol available beyond the description in the main text?"
  * "Is information provided on how to obtain unique materials or reagents?"
  * "Are details about the computational environment needed for reproducibility provided?"
  * "Are any companies, industry partners, or technology transfer offices mentioned in relation to commercial applications of the research?"
  * "Is there information about licensing, patents, or commercialization agreements related to the research outputs?"

### 5.7 Method Execution Component

* **Definition:** Represents a specific instance or run of the planned Procedure. Captures details unique to that execution, essential for provenance tracking and understanding variations from the plan.
* **Properties/Sub-components:**
  * executionID (URI or String: Unique identifier for this specific run)
  * correspondsToPlan (Link to the Procedure component representing the plan/template). Links SO:Activity to SO:Method [22], RO:wfprov:WorkflowRun to RO:wfdesc:WorkflowTemplate [23]
  * executionDateTime (Timestamp or Date Range)
  * executor (Link to Actor or String: Person or system performing the execution)
  * parameterValuesUsed (List of key-value pairs specifying actual settings used, potentially overriding defaults in the plan)
  * executionEnvironment (String: Specific lab conditions, software versions used in this run, hardware details)
  * deviationsFromPlan (String: Description of any differences between this execution and the planned procedure)
  * producedData (Link to specific output datasets or results generated by this instance). Links to wfprov:Artifact [23]
  * executionLog (URI or String: Link to detailed logs, if available)

* **Illustrative Examples:**
  * (Lab Run): executionID: "ExpA_Run_20240115"; correspondsToPlan: [link to Protocol Z]; executionDateTime: "2024-01-15T10:00:00Z"; executor: "LabTech_JS"; parameterValuesUsed: {"IncubationTime": "32min"}; deviationsFromPlan: "Incubation time extended due to equipment delay"
  * (Workflow Run): executionID: [URI]; correspondsToPlan: [URI]; executionDateTime: "Timestamp"; producedData: [URI]. Links to wfprov concepts [23]
* **Guiding Questions:**
  * "Does the paper describe specific runs or instances of the experiment/analysis (beyond the general method)?"
  * "Are specific dates, times, or execution identifiers mentioned?"
  * "Are variations in parameters or conditions across different runs reported?"
  * "Are deviations from the standard protocol noted for specific instances?"
  * "Can specific output datasets be linked to specific executions of the method? (Crucial for provenance [23])"

## 6. Discussion

### 6.1 Integration Benefits

The Scientific Knowledge Extraction Ontology (SKEO) offers several key benefits through its integration of scientific methods, opportunities, and challenges into a unified framework:

* **Holistic Research Representation:** By combining methodological details with the driving forces (opportunities) and impediments (challenges) of research, SKEO provides a more complete picture of the scientific process than any single existing ontology. This holistic approach acknowledges that methods are chosen in response to specific problems and opportunities, and are constrained by particular challenges [6].

* **Cross-domain Applicability:** The ontology is designed to be applicable across diverse scientific disciplines while maintaining sufficient specificity to capture domain-relevant details. This balance is achieved through a combination of domain-agnostic high-level concepts with extensible properties that can accommodate field-specific information [8].

* **Lifecycle Coverage:** The framework encompasses the entire research lifecycle, from theoretical foundations and problem formulation through methodological execution to findings and future directions. This comprehensive coverage supports a deeper understanding of how scientific knowledge evolves over time [4].

* **Enhanced Knowledge Discovery:** By structuring information about opportunities and challenges alongside methodological details, the ontology enables novel connections to be discovered. For example, researchers could identify methods that have been successfully applied to similar challenges across different domains, or recognize patterns in how certain types of limitations lead to specific future research directions [1].

* **Improved Machine Actionability:** The structured representation of methods, opportunities, and challenges makes this information more accessible to computational tools, supporting automated reasoning, comparison, and analysis that would be difficult with traditional narrative descriptions [3].

### 6.2 Applications

The SKEO has significant potential for various applications aimed at enhancing scientific research and communication:

#### 6.2.1 Knowledge Management and Discovery

* **Comprehensive Knowledge Bases:** SKEO can serve as the schema for knowledge bases that integrate methodological information with research problems, opportunities, and challenges, allowing structured storage, querying, and retrieval across studies and disciplines [6].

* **Enhanced Scientific Search:** Search tools incorporating this ontology could allow users to filter or search for papers based on specific methodological features, challenges addressed, or opportunities presented, going far beyond simple keyword searching [6].

* **Research Landscape Analysis:** By applying the taxonomy across large corpora of scientific literature, researchers and policymakers can analyze trends in identified opportunities, map the landscape of persistent challenges within fields, and potentially identify emerging research areas [19].

#### 6.2.2 Research Planning and Execution

* **Methodology Selection Support:** Researchers could query for methodological approaches that have been successfully applied to similar problems or that address particular types of challenges, helping to inform study design decisions [8].

* **Anticipated Challenge Mitigation:** By structuring information about common challenges associated with specific methodological approaches, the ontology could help researchers anticipate and plan for potential difficulties [23].

* **Research Quality Enhancement:** The detailed representation of validation procedures, limitations, and reproducibility provisions could help researchers implement more rigorous methods and more transparent reporting [3].

#### 6.2.3 Scientific Communication and Review

* **Structured Reporting:** The ontology could underpin templates for structured methods reporting in journals, grant applications, or data repositories, promoting completeness and consistency [15].

* **Systematic Review Support:** Researchers conducting systematic reviews or meta-analyses can use the taxonomy as a coding framework to systematically categorize information about methods, gaps, limitations, challenges, and future work identified in the reviewed papers [33].

* **Peer Review Enhancement:** Reviewers could use the structured representation to systematically assess methodological completeness, identification of limitations, and alignment between challenges, methods, and opportunities [6].

#### 6.2.4 Computational Applications

* **AI/NLP Model Training:** The ontology provides a structured target vocabulary for training Natural Language Processing (NLP) and Machine Learning (ML) models to automatically extract comprehensive information about scientific research from texts [4].

* **Workflow Systems Integration:** The method representation could be integrated with scientific workflow systems to support better documentation, execution tracking, and provenance capture [23].

* **Automated Knowledge Extraction:** Structured extraction of methods, opportunities, and challenges could support automated literature analysis, hypothesis generation, or research trend identification [5].

### 6.3 Implementation Considerations

Realizing the benefits of SKEO requires addressing several practical implementation challenges:

* **Ontology Language and Formalism:** Utilizing a standard, expressive language like OWL 2 DL (Web Ontology Language) is recommended for formal rigor, compatibility with semantic web tools, and reasoning capabilities [9].

* **Tooling Development:** User-friendly tools are essential for both annotating scientific papers or protocols according to the ontology and for querying the resulting knowledge base. This includes interfaces for manual annotation, potentially semi-automated extraction tools, and intuitive query builders [6].

* **Annotation Methodology:** Effectively populating knowledge structures often requires methodologies that optimally combine human expertise and machine capabilities, potentially involving human-in-the-loop approaches or collaborative annotation platforms [32].

* **Integration with Existing Systems:** SKEO should ideally integrate with existing infrastructure, such as electronic laboratory notebooks (ELNs), data repositories (e.g., linking data descriptions to the methods that produced them), workflow systems (e.g., mapping workflow language elements to ontology concepts), and potentially publication platforms [3].

* **Community Engagement:** Widespread adoption requires community engagement, clear demonstration of value, and potentially integration into existing research workflows. Training for researchers, curators, and developers on using the ontology is crucial [37].

* **Governance and Maintenance:** Establishing clear governance and maintenance processes is vital for keeping the ontology relevant and accurate over time as scientific practices evolve [31].

### 6.4 Limitations and Future Work

Despite its comprehensive approach, SKEO has limitations that warrant consideration and suggest avenues for future development:

* **Granularity vs. Usability Trade-off:** The ontology aims to balance comprehensiveness with practical usability, but some domains may require additional specialized concepts or properties. Future work could involve developing domain-specific extensions while maintaining compatibility with the core ontology [8].

* **Validation Requirements:** The proposed ontology requires empirical validation through annotation studies with human experts across different scientific domains to assess its clarity, comprehensiveness, and inter-annotator reliability [37].

* **Automated Extraction Challenges:** While the ontology provides a target for AI/NLP models, accurately extracting these elements automatically from unstructured text remains challenging, potentially requiring sophisticated models and suffering from noise or limited quality, especially for vaguely defined concepts [1].

* **Integration with Upper Ontologies:** Future work should include formal alignment with established upper ontologies like BFO or SUMO to enhance interoperability with other scientific ontologies [8].

* **Representation of Complex Relationships:** Some complex relationships between challenges, methods, and opportunities might not be fully captured by the current model. Future iterations could incorporate more sophisticated relationship types and constraints [14].

Future directions should include:

* Developing specific domain extensions (e.g., for clinical trials, specific types of simulations, qualitative methodologies)
* Creating and evaluating tools for semi-automated annotation of publications based on SKEO
* Building validation tools to check the consistency and completeness of ontology-based descriptions
* Conducting large-scale annotation projects to populate knowledge bases and demonstrate utility
* Exploring deeper integration with provenance models like PROV-O and workflow execution systems
* Establishing community governance structures for ongoing maintenance and development

## 7. Conclusion

The systematic description of scientific research—encompassing methods, opportunities, and challenges—is paramount for ensuring transparency, reproducibility, and cumulative progress of science. Current narrative approaches, while necessary, are often insufficient for detailed comparison, computational analysis, and rigorous assessment. This report has proposed the Scientific Knowledge Extraction Ontology (SKEO), an integrated framework designed to address these limitations.

SKEO synthesizes key concepts from existing ontologies (SO, RO, EXPO, SemSur, ORKG) and extends them to provide a comprehensive structure for representing the full context of scientific research. The ontology is organized around three main branches: (1) methodological framework components that detail how research is conducted, (2) scientific opportunity components that capture forward-looking aspects like knowledge gaps and future directions, and (3) scientific challenge components that describe obstacles and limitations.

The ontology maintains crucial distinctions, such as the separation between planned methods and their execution instances, while adding the novel dimension of explicitly classifying different types of opportunities and challenges. Each component is defined with specific properties and guiding questions to facilitate the extraction and representation of information from scientific sources.

The value of SKEO lies in its potential to create structured, machine-readable knowledge bases of scientific research. This can significantly enhance semantic search, enable systematic methodological comparisons, support reproducibility assessments, facilitate meta-analysis, and empower AI applications in science. By providing a common, detailed vocabulary for describing the 'how', 'why', and 'what if' of scientific investigation, SKEO represents a crucial step towards fostering greater rigor, collaboration, and accelerated discovery in the increasingly complex landscape of modern science.

Future work should focus on validating the ontology across diverse domains, developing tools to support its adoption, and creating methodologies for efficiently populating knowledge bases using this comprehensive framework. Through these efforts, the vision of more FAIR (Findable, Accessible, Interoperable, and Reusable) scientific knowledge can be more fully realized.

## References

1. [University Libraries and the Open Research Knowledge Graph](https://docs.lib.purdue.edu/context/iatul/article/2334/viewcontent/University_Libraries_and_the_Open_Research_Knowledge_Graph.pdf). Purdue e-Pubs.
2. [SemSur: A Core Ontology for the Semantic Representation of Research Findings](https://www.researchgate.net/publication/323167072_SemSur_A_Core_Ontology_for_the_Semantic_Representation_of_Research_Findings). ResearchGate.
3. [The Research Object Suite of Ontologies: Sharing and Exchanging Research Data and Methods on the Open Web](https://pure.manchester.ac.uk/ws/files/29281737/PRE-PEER-REVIEW.PDF). University of Manchester.
4. [Smith, B. Ontology (science)](https://philarchive.org/rec/SMIOS). PhilArchive.
5. [Exposé: An Ontology for Data Mining Experiments](https://lirias.kuleuven.be/retrieve/118733). Lirias.
6. [Scholarly Ontology](http://isdb.cs.aueb.gr/scholarlyontology/). AUEB ISDB LAB.
7. [Large Language Models for Scholarly Ontology Generation: An Extensive Analysis in the Engineering Field](https://arxiv.org/abs/2412.08258). arXiv.
8. [An ontology of scientific experiments](https://pmc.ncbi.nlm.nih.gov/articles/PMC1885356/). PMC.
9. [An ontology for a Robot Scientist](https://pure.aber.ac.uk/ws/files/71102/An%20ontology%20for%20a%20Robot%20Scientist.pdf). Aberystwyth University.
10. [EXPO ontology](https://expo.sourceforge.net/). SourceForge.
11. [An Ontology of Scientific Experiments](https://www.researchgate.net/publication/6780382_An_Ontology_of_Scientific_Experiments). ResearchGate.
12. [An ontology of scientific experiments](https://royalsocietypublishing.org/doi/10.1098/rsif.2006.0134). Journal of The Royal Society Interface.
13. [Understanding and Applying Research Paradigms in Educational Contexts](https://files.eric.ed.gov/fulltext/EJ1154775.pdf). ERIC.
14. [Ontology (information science)](https://en.wikipedia.org/wiki/Ontology_(information_science)). Wikipedia.
15. [Designing a Metadata Ontology Model for Semantic Modeling and Representation of Scholarly Journal Articles: A Case Study of ISC Journals](https://ijism.isc.ac/article_716224_8b4fb643df2eed24974242e6771b0d1d.pdf).
16. [A Methodology to Develop Ontologies for Emerging Domains](https://files.eric.ed.gov/fulltext/EJ1100556.pdf). ERIC.
17. [Applications of ontologies in requirements engineering: a systematic review of the literature](https://www.researchgate.net/publication/272238071_Applications_of_ontologies_in_requirements_engineering_a_systematic_review_of_the_literature). ResearchGate.
18. [Ontology-based data modeling for cultural heritage](https://www.lestudium-ias.com/system/files/Sanfilippo_LeStudiumJournal.pdf). Le Studium Loire Valley Institute for Advanced Studies.
19. [Brainmap taxonomy of experimental design: Description and evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6871758/). PMC.
20. [A Model for the Taxonomy of Research Studies: A Practical Guide to Knowledge Production and Knowledge Management](https://brieflands.com/articles/apid-112456). Brieflands.
21. [What is a Conceptual Framework and How to Make It (with examples)](https://researcher.life/blog/article/what-is-a-conceptual-framework-and-how-to-make-it-with-examples/). Researcher.life.
22. [Scholarly Ontology](https://github.com/athenarc/scholarly-ontology). GitHub.
23. [A Suite of Ontologies for Preserving Workflow Research Objects](https://vocab.linkeddata.es/ro-jws/). vocab.linkeddata.es.
24. [Wf4Ever Research Object Ontologies and Vocabularies Primer](http://wf4ever.github.io/ro-primer/). wf4ever.github.io.
25. [A Taxonomy for the Analysis of Scientific Workflow Faults](https://www.researchgate.net/publication/224212613_A_Taxonomy_for_the_Analysis_of_Scientific_Workflow_Faults). ResearchGate.
26. [Reference Taxonomy of Clinical Workflows](https://www.healthit.gov/sites/default/files/cds/3_5_7_workflow_implementation_tool_user_guide_508.pdf). Office of the National Coordinator for Health Information Technology (ONC).
27. [Basic Research Needs for Environmental Management](https://www.pnnl.gov/main/publications/external/technical_reports/PNNL-25166.pdf). Pacific Northwest National Laboratory.
28. [Carrying out research across the arts and humanities and social sciences: developing the methodology for Dementia and Imagination](https://www.researchgate.net/publication/309134891_Carrying_out_research_across_the_arts_and_humanities_and_social_sciences_developing_the_methodology_for_Dementia_and_Imagination). ResearchGate.
29. [OSF.io](https://osf.io/nua9s/download).
30. [Seeking outsider perspectives in interpretive research: young adults and citizen participation in health policy](https://www.tandfonline.com/doi/full/10.1080/19460171.2014.951667). Taylor & Francis Online.
31. [WP4 - final report informal media education in Europe](https://eavi.eu/wp-content/uploads/2017/02/WP4-Final-report-1.pdf). EAVI.
32. [Perspectives on Ontology Learning](https://jens-lehmann.org/files/2014/perspectives_on_ontology_learning.pdf). Jens Lehmann.
33. [Challenges in assessing the effects of environmental governance systems on conservation outcomes](https://www.researchgate.net/publication/385004254_Challenges_in_assessing_the_effects_of_environmental_governance_systems_on_conservation_outcomes). ResearchGate.
34. [The Use of Machine Learning Algorithms in the Classification of Sound](https://ugspace.ug.edu.gh/server/api/core/bitstreams/35bd8ca2-5cc2-4c73-a579-f4cc54f914a7/content). UGSpace.
35. [Core.ac.uk](https://core.ac.uk/download/pdf/301352899.pdf).
36. [Eye Tracking the User Experience - An Evaluation of Ontology Visualization Techniques](https://www.semantic-web-journal.net/system/files/swj861_0.pdf). Semantic Web Journal.
37. [Developing and using ontologies in behavioural science: addressing issues raised](https://pmc.ncbi.nlm.nih.gov/articles/PMC11109559/). PMC.
38. [A Domain Reference Ontology for Design Science Research Knowledge Bases](https://www.researchgate.net/publication/382307290_A_Domain_Reference_Ontology_for_Design_Science_Research_Knowledge_Bases). ResearchGate.
39. [Common Source Bias, Key Informants, and Survey-Administrative Linked Data for Nonprofit Management Research](https://www.researchgate.net/publication/335776040_Common_Source_Bias_Key_Informants_and_Survey-Administrative_Linked_Data_for_Nonprofit_Management_Research). ResearchGate.
40. [DOCTORAL THESIS](https://upcommons.upc.edu/bitstream/handle/2117/369388/TNC1de1.pdf;jsessionid=2481A6A39696D06A32E73065D4391B53?sequence=1). UPCommons.
