# skeo_models.py - Pydantic models defining the SKEO schema

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Any, Optional

# Note: All 'id' fields and relationship fields (like 'paper', 'relatedProblem')
# are now Optional[str] to accommodate UUIDs.

class Author(BaseModel):
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None
    isCorresponding: bool = False

class FundingSource(BaseModel):
    funderName: str
    grantNumber: Optional[str] = None
    grantTitle: Optional[str] = None

class Institution(BaseModel):
    name: str
    location: Optional[str] = None
    role: Optional[str] = None

class ResearchContext(BaseModel):
    discipline: Optional[str] = None
    fieldOfStudy: Optional[str] = None
    associatedProject: Optional[str] = None
    fundingSources: Optional[List[FundingSource]] = []
    institutions: Optional[List[Institution]] = []
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None

class TheoryReference(BaseModel):
    theoryName: str
    originators: Optional[str] = None
    relevance: Optional[str] = None

class ModelReference(BaseModel):
    modelName: str
    modelType: Optional[str] = None
    relevance: Optional[str] = None

class TheoreticalBasis(BaseModel):
    underlyingTheories: Optional[List[TheoryReference]] = []
    conceptualFrameworkReference: Optional[str] = None
    guidingModels: Optional[List[ModelReference]] = []
    philosophicalParadigm: Optional[str] = None
    schoolOfThought: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None

class ResearchProblem(BaseModel):
    problemStatement: str
    problemScope: Optional[str] = None
    problemType: Optional[str] = None
    problemImportance: Optional[str] = None
    businessRelevance: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None

class KnowledgeGap(BaseModel):
    gapDescription: str
    relatedDomain: Optional[str] = None
    gapSignificance: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    relatedProblem: Optional[str] = None

class VariableReference(BaseModel):
    variableName: str
    variableRole: Optional[str] = None

class ResearchQuestion(BaseModel):
    questionText: str
    questionType: Optional[str] = None
    relatedVariables: Optional[List[VariableReference]] = []
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    relatedProblem: Optional[str] = None
    addressesGap: Optional[str] = None

class FutureDirection(BaseModel):
    directionDescription: str
    timeframe: Optional[str] = None
    requiredResources: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    addressesGap: Optional[str] = None
    arisesFromLimitation: Optional[str] = None
    extendsPotentialApplication: Optional[str] = None

class PotentialApplication(BaseModel):
    applicationDescription: str
    targetSector: Optional[str] = None
    implementationReadiness: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    buildOnMethodologicalFrameworks: Optional[List[str]] = []

class ScientificChallenge(BaseModel):
    challengeDescription: str
    challengeType: Optional[str] = None
    severity: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    relatedProblem: Optional[str] = None

class MethodologicalChallenge(BaseModel):
    challengeDescription: str
    researchPhase: Optional[str] = None
    mitigationStrategy: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    relatedScientificChallenge: Optional[str] = None
    encounteredInFramework: Optional[str] = None
    resultsInLimitation: Optional[str] = None

class ImplementationChallenge(BaseModel):
    challengeDescription: str
    resourceConstraint: Optional[str] = None
    technicalHurdle: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    relatedApplication: Optional[str] = None
    encounteredInFramework: Optional[str] = None

class Limitation(BaseModel):
    limitationDescription: str
    limitationType: Optional[str] = None
    impactOnFindings: Optional[str] = None
    businessConstraints: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    limitedFramework: Optional[str] = None

class StudyDesign(BaseModel):
    designType: str
    controlGroup: bool = False
    randomization: bool = False
    blinding: Optional[str] = None
    timeDimension: Optional[str] = None
    designDetails: Optional[str] = None

class PopulationSampling(BaseModel):
    targetPopulation: Optional[str] = None
    samplingFrame: Optional[str] = None
    sampleSize: Optional[int] = None # Keep int if sample size is always number
    samplingMethod: Optional[str] = None
    inclusionCriteria: Optional[str] = None
    exclusionCriteria: Optional[str] = None
    responseRate: Optional[float] = None

class Variable(BaseModel):
    variableName: str
    variableRole: Optional[str] = None
    conceptualDefinition: Optional[str] = None
    operationalization: Optional[str] = None
    measurementScale: Optional[str] = None
    units: Optional[str] = None

class ProcedureStep(BaseModel):
    stepNumber: Optional[int] = None
    description: str
    inputs: Optional[str] = None
    outputs: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    controlFlow: Optional[str] = None

class Procedure(BaseModel):
    procedureName: str
    version: Optional[str] = None
    steps: Optional[List[ProcedureStep]] = []
    procedureDescription: Optional[str] = None

class DataCollection(BaseModel):
    collectionMethod: Optional[str] = None
    instrumentDescription: Optional[str] = None
    collectionSetting: Optional[str] = None
    collectionTimeframe: Optional[str] = None
    dataRecordingFormat: Optional[str] = None
    collectionProcedureDetails: Optional[str] = None

class DataAnalysis(BaseModel):
    analysisApproach: Optional[str] = None
    statisticalTests: Optional[str] = None
    algorithmsUsed: Optional[str] = None
    softwareDetails: Optional[str] = None
    parameterSettings: Optional[str] = None
    dataPreprocessingSteps: Optional[str] = None
    analysisDetails: Optional[str] = None

class ResultsRepresentation(BaseModel):
    representationFormat: Optional[str] = None
    visualizationType: Optional[str] = None
    reportingStandard: Optional[str] = None
    primaryOutcomeMeasure: Optional[str] = None

class ValidationVerification(BaseModel):
    validationTypes: Optional[List[str]] = []
    validationProcedure: Optional[str] = None
    validationMetrics: Optional[str] = None
    validationResults: Optional[str] = None
    industryStandards: Optional[str] = None

class EthicalConsiderations(BaseModel):
    ethicsApprovalBody: Optional[str] = None
    approvalIdentifier: Optional[str] = None
    informedConsentProcedure: Optional[str] = None
    animalWelfareCompliance: Optional[str] = None
    dataAnonymization: Optional[bool] = None
    privacyMeasures: Optional[str] = None

class ReproducibilitySharing(BaseModel):
    dataAvailabilityStatement: Optional[str] = None
    dataRepository: Optional[str] = None
    dataAccessionNumber: Optional[str] = None
    codeAvailabilityStatement: Optional[str] = None
    codeRepository: Optional[str] = None
    protocolAvailability: Optional[str] = None
    materialsAvailability: Optional[str] = None
    softwareEnvironment: Optional[str] = None
    commercializationPartners: Optional[str] = None

class MaterialTool(BaseModel):
    itemName: str
    itemType: Optional[str] = None
    identifier: Optional[str] = None
    specifications: Optional[str] = None
    roleInProcedure: Optional[str] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    usedInFrameworks: Optional[List[str]] = []
    usedInExecutions: Optional[List[str]] = []

class MethodologicalFramework(BaseModel):
    name: str
    description: Optional[str] = None
    studyDesign: Optional[StudyDesign] = None # Optional study design
    populationAndSampling: Optional[PopulationSampling] = None
    variables: Optional[List[Variable]] = []
    procedures: Optional[List[Procedure]] = []
    dataCollection: Optional[DataCollection] = None
    dataAnalysis: Optional[DataAnalysis] = None
    resultsRepresentation: Optional[ResultsRepresentation] = None
    validationAndVerification: Optional[ValidationVerification] = None
    ethicalConsiderations: Optional[EthicalConsiderations] = None
    reproducibilityAndSharing: Optional[ReproducibilitySharing] = None
    extractionConfidence: float = Field(default=0.7, ge=0, le=1)
    id: Optional[str] = None
    paper: Optional[str] = None
    researchProblem: Optional[str] = None
    materialsAndTools: Optional[List[str]] = []

class ScientificPaper(BaseModel):
    title: str
    authors: Optional[List[Author]] = []
    abstract: Optional[str] = None
    doi: Optional[str] = None
    publicationDate: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    keywords: Optional[List[str]] = []
    pdfPath: Optional[str] = None
    fileUrl: Optional[str] = None
    vectorEmbedding: Optional[List[float]] = None # Placeholder
    extractionDate: Optional[str] = None
    extractionConfidenceScore: Optional[float] = Field(default=0.0, ge=0, le=1)
    id: Optional[str] = None # Internal UUID