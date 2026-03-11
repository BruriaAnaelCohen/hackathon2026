-- ===================================================================
-- Books Table Setup
-- ===================================================================

USE HACKATHON2026;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Books')
BEGIN
    CREATE TABLE Books (
        BookID INT IDENTITY(1,1) PRIMARY KEY,
        BookName NVARCHAR(200) NOT NULL,
        AuthorName NVARCHAR(200),
        PublishYear INT,
        ShortSummary NVARCHAR(MAX),
        GeneralReview NVARCHAR(MAX),
        Rating DECIMAL(2,1),
        
        -- AI generated columns
        ai_genre NVARCHAR(100),
        ai_is_favorite BIT NULL,
        ai_target_audience NVARCHAR(200) NULL
    );
    PRINT 'Table Books created successfully.';
END
ELSE
BEGIN
    PRINT 'Table Books already exists.';
END
GO
