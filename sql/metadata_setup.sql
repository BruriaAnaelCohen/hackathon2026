-- ===================================================================
-- AI Metadata Tables Setup
-- ===================================================================

USE HACKATHON2026;
GO

-- ===================================================================
-- Table: AI_Projects
-- Stores project metadata for AI enrichment tasks
-- ===================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AI_Projects')
BEGIN
    CREATE TABLE AI_Projects (
        ProjectID INT IDENTITY(1,1) PRIMARY KEY,
        ProjectName NVARCHAR(255) NOT NULL UNIQUE,
        ServerName NVARCHAR(100) NULL,
        DatabaseName NVARCHAR(100) NULL,
        TableName NVARCHAR(100) NULL,
        Description NVARCHAR(MAX) NULL,
        CreatedDate DATETIME DEFAULT GETDATE(),
        Status NVARCHAR(50) DEFAULT 'Active'
    );
    PRINT 'Table AI_Projects created successfully.';
END
ELSE
BEGIN
    PRINT 'Table AI_Projects already exists.';
END
GO

-- ===================================================================
-- Table: AI_Processes
-- Stores processing tasks for each project (categorize/enrich)
-- ===================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AI_Processes')
BEGIN
    CREATE TABLE AI_Processes (
        ProcessID INT IDENTITY(1,1) PRIMARY KEY,
        ProjectID INT NOT NULL,
        ProcessType NVARCHAR(20) NOT NULL, -- 'Categorize' or 'Enrich'
        TaskDescription NVARCHAR(500) NOT NULL,
        SourceColumn NVARCHAR(100) NOT NULL,
        SourceColumnDescription NVARCHAR(255) NULL,
        DestColumn NVARCHAR(100) NULL, -- Destination column for results
        AdditionalColumns NVARCHAR(MAX) NULL, -- JSON array of column names
        ExpectedOutput NVARCHAR(500) NOT NULL,
        MaxCategories INT NULL, -- Limit for categorization
        CreatedDate DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (ProjectID) REFERENCES AI_Projects(ProjectID) ON DELETE CASCADE
    );
    PRINT 'Table AI_Processes created successfully.';
END
ELSE
BEGIN
    PRINT 'Table AI_Processes already exists.';
END

-- Add DestColumn if it doesn't exist (for existing tables)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('AI_Processes') AND name = 'DestColumn')
BEGIN
    ALTER TABLE AI_Processes ADD DestColumn NVARCHAR(100) NULL;
    PRINT 'Column DestColumn added to AI_Processes.';
END
GO

-- ===================================================================
-- Table: AI_Categories
-- Stores generated categories for categorization tasks
-- ===================================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AI_Categories')
BEGIN
    CREATE TABLE AI_Categories (
        CategoryID INT IDENTITY(1,1) PRIMARY KEY,
        ProcessID INT NOT NULL,
        CategoryName NVARCHAR(255) NOT NULL,
        FOREIGN KEY (ProcessID) REFERENCES AI_Processes(ProcessID) ON DELETE CASCADE
    );
    PRINT 'Table AI_Categories created successfully.';
END
ELSE
BEGIN
    PRINT 'Table AI_Categories already exists.';
END
GO

-- ===================================================================
-- Create indexes for better performance
-- ===================================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_AI_Processes_ProjectID' AND object_id = OBJECT_ID('AI_Processes'))
BEGIN
    CREATE INDEX IX_AI_Processes_ProjectID ON AI_Processes(ProjectID);
    PRINT 'Index IX_AI_Processes_ProjectID created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_AI_Categories_ProcessID' AND object_id = OBJECT_ID('AI_Categories'))
BEGIN
    CREATE INDEX IX_AI_Categories_ProcessID ON AI_Categories(ProcessID);
    PRINT 'Index IX_AI_Categories_ProcessID created.';
END
GO

PRINT '===============================================';
PRINT 'AI Metadata Tables Setup Complete!';
PRINT '===============================================';
