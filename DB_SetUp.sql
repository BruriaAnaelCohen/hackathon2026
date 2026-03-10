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




INSERT INTO Books
(BookName, AuthorName, PublishYear, ShortSummary, GeneralReview, Rating, ai_genre, ai_is_favorite, ai_target_audience)
VALUES
('1984','George Orwell',1949,
'A dystopian novel about a totalitarian regime that controls every aspect of life. Winston Smith quietly rebels against a system built on surveillance and manipulation of truth.',
'A chilling and powerful story with sharp political insight, though its bleak atmosphere can feel emotionally exhausting.',
4.6,NULL,NULL,NULL),

('To Kill a Mockingbird','Harper Lee',1960,
'A young girl in the American South watches her father defend a Black man falsely accused of a crime, revealing injustice and moral courage.',
'A beautifully written novel with memorable characters and strong moral themes.',
4.7,NULL,NULL,NULL),

('The Great Gatsby','F. Scott Fitzgerald',1925,
'Nick Carraway observes the mysterious millionaire Jay Gatsby and his obsession with Daisy Buchanan in a world of wealth and illusion.',
'The prose is elegant and symbolic, but some readers find the characters distant and hard to connect with.',
4.2,NULL,NULL,NULL),

('Pride and Prejudice','Jane Austen',1813,
'Elizabeth Bennet navigates family pressures, social expectations, and her evolving relationship with Mr. Darcy.',
'Witty dialogue and sharp social observation make this a classic that still feels lively today.',
4.6,NULL,NULL,NULL),

('The Hobbit','J.R.R. Tolkien',1937,
'Bilbo Baggins joins a band of dwarves on an adventure to reclaim treasure guarded by the dragon Smaug.',
'A charming and imaginative adventure that is easy to enjoy even decades later.',
4.7,NULL,NULL,NULL),

('The Catcher in the Rye','J.D. Salinger',1951,
'Teenager Holden Caulfield wanders through New York reflecting on loneliness, growing up, and the hypocrisy he sees around him.',
'The narrative voice is distinctive, but the story can feel repetitive and the protagonist frustrating.',
3.9,NULL,NULL,NULL),

('The Lord of the Rings','J.R.R. Tolkien',1954,
'Frodo Baggins and his companions attempt to destroy a powerful ring before it can be used by the dark lord Sauron.',
'An epic world filled with depth and imagination, though the lengthy descriptions slow the pace at times.',
4.8,NULL,NULL,NULL),

('Harry Potter and the Sorcerer''s Stone','J.K. Rowling',1997,
'Harry Potter discovers he is a wizard and begins his first year at Hogwarts School of Witchcraft and Wizardry.',
'A magical and engaging start to the series that captures a sense of wonder.',
4.7,NULL,NULL,NULL),

('The Da Vinci Code','Dan Brown',2003,
'A symbologist investigates a murder in the Louvre and follows clues tied to secret religious societies.',
'A fast-paced thriller that keeps the pages turning, even if the writing itself is fairly simple.',
3.9,NULL,NULL,NULL),

('The Alchemist','Paulo Coelho',1988,
'A shepherd named Santiago travels across the desert searching for treasure and learning about destiny.',
'The message is inspiring, but the storytelling can feel overly simple.',
4.1,NULL,NULL,NULL),

('The Hunger Games','Suzanne Collins',2008,
'Katniss Everdeen volunteers to take her sister’s place in a deadly televised competition.',
'A gripping dystopian story with strong tension and memorable moments.',
4.4,NULL,NULL,NULL),

('Brave New World','Aldous Huxley',1932,
'A futuristic society built on genetic engineering and constant pleasure hides deep questions about freedom.',
'A thought-provoking concept, though the emotional distance between characters can weaken the story.',
4.2,NULL,NULL,NULL),

('Animal Farm','George Orwell',1945,
'Farm animals overthrow their human owner but slowly recreate the same oppressive system.',
'Short, sharp, and brilliantly satirical.',
4.5,NULL,NULL,NULL),

('The Kite Runner','Khaled Hosseini',2003,
'A man reflects on his childhood in Afghanistan and the betrayal that shaped his life.',
'An emotionally powerful novel that leaves a lasting impression.',
4.6,NULL,NULL,NULL),

('Life of Pi','Yann Martel',2001,
'A boy survives a shipwreck and drifts across the ocean on a lifeboat with a tiger.',
'A creative and philosophical story, though the ending divides readers.',
4.1,NULL,NULL,NULL),

('The Girl with the Dragon Tattoo','Stieg Larsson',2005,
'A journalist and a hacker investigate the disappearance of a wealthy family’s daughter.',
'A dark and gripping mystery, but the opening chapters move slowly.',
4.2,NULL,NULL,NULL),

('Gone Girl','Gillian Flynn',2012,
'A marriage collapses after a woman disappears and suspicion falls on her husband.',
'Clever twists and a dark tone make it difficult to put down.',
4.1,NULL,NULL,NULL),

('Dune','Frank Herbert',1965,
'Paul Atreides becomes involved in a complex political struggle on the desert planet Arrakis.',
'An ambitious and richly detailed world, though the complexity can overwhelm new readers.',
4.6,NULL,NULL,NULL),

('The Fault in Our Stars','John Green',2012,
'Two teenagers with cancer form a deep bond while confronting love and mortality.',
'Touching and heartfelt, but sometimes a little sentimental.',
4.2,NULL,NULL,NULL),

('The Book Thief','Markus Zusak',2005,
'A girl in Nazi Germany discovers the power of words while living with a foster family.',
'Beautifully written and deeply moving.',
4.6,NULL,NULL,NULL),

('Dracula','Bram Stoker',1897,
'A vampire from Transylvania threatens Victorian England.',
'Atmospheric and influential, though the pacing can feel uneven.',
4.1,NULL,NULL,NULL),

('Frankenstein','Mary Shelley',1818,
'A scientist creates life through an experiment and must face the consequences.',
'A fascinating exploration of ambition and responsibility.',
4.4,NULL,NULL,NULL),

('The Shining','Stephen King',1977,
'A family isolated in a haunted hotel slowly falls apart under supernatural influence.',
'Slow build-up but extremely tense and memorable.',
4.3,NULL,NULL,NULL),

('The Road','Cormac McCarthy',2006,
'A father and son travel through a bleak post-apocalyptic world.',
'The writing is powerful, but the story is relentlessly grim.',
4.1,NULL,NULL,NULL),

('The Martian','Andy Weir',2011,
'An astronaut stranded on Mars must survive using science and ingenuity.',
'Smart, funny, and full of clever problem-solving.',
4.5,NULL,NULL,NULL),

('Jurassic Park','Michael Crichton',1990,
'Scientists create a theme park filled with cloned dinosaurs.',
'An exciting idea that blends science with thriller pacing.',
4.2,NULL,NULL,NULL),

('The Handmaid''s Tale','Margaret Atwood',1985,
'A woman struggles to survive in a regime where women have lost their rights.',
'Disturbing but incredibly relevant and powerful.',
4.3,NULL,NULL,NULL),

('Slaughterhouse-Five','Kurt Vonnegut',1969,
'A soldier moves unpredictably through time, revisiting the trauma of war.',
'Original and darkly humorous, though the nonlinear structure may confuse some readers.',
4.1,NULL,NULL,NULL),

('Fahrenheit 451','Ray Bradbury',1953,
'A firefighter begins questioning a society where books are banned.',
'Thought-provoking and haunting.',
4.4,NULL,NULL,NULL),

('The Color Purple','Alice Walker',1982,
'A woman writes letters describing her struggle for independence and dignity.',
'A deeply emotional and important story.',
4.3,NULL,NULL,NULL),

('Rebecca','Daphne du Maurier',1938,
'A young woman becomes haunted by the memory of her husband’s first wife.',
'A slow but gripping psychological story.',
4.2,NULL,NULL,NULL),

('Of Mice and Men','John Steinbeck',1937,
'Two migrant workers chase a dream of owning land during the Great Depression.',
'Short, simple, and heartbreaking.',
4.4,NULL,NULL,NULL),

('A Game of Thrones','George R.R. Martin',1996,
'Noble families fight for power in a brutal fantasy world.',
'Complex characters and political intrigue make the story compelling.',
4.6,NULL,NULL,NULL),

('The Name of the Wind','Patrick Rothfuss',2007,
'Kvothe recounts his journey from gifted child to legendary figure.',
'Rich storytelling and atmosphere, though the pacing can wander.',
4.5,NULL,NULL,NULL),

('The Night Circus','Erin Morgenstern',2011,
'A magical circus becomes the arena for a mysterious rivalry.',
'Atmospheric and imaginative, but the plot moves slowly.',
4.0,NULL,NULL,NULL),

('Ready Player One','Ernest Cline',2011,
'A teenager competes in a virtual reality treasure hunt.',
'Fun and nostalgic, though packed with references that not everyone enjoys.',
4.1,NULL,NULL,NULL),

('The Silent Patient','Alex Michaelides',2019,
'A therapist becomes obsessed with a woman who stopped speaking after killing her husband.',
'A clever twist at the end, but the characters sometimes feel shallow.',
4.0,NULL,NULL,NULL),

('The Secret Garden','Frances Hodgson Burnett',1911,
'A lonely girl discovers a neglected garden that slowly transforms the lives around her.',
'A gentle and hopeful story.',
4.0,NULL,NULL,NULL),

('The Outsiders','S.E. Hinton',1967,
'Teenagers from rival groups struggle with identity and loyalty.',
'A simple but very honest portrayal of youth.',
4.2,NULL,NULL,NULL),

('The Chronicles of Narnia','C.S. Lewis',1950,
'Children discover a magical world where they become part of a battle between good and evil.',
'Creative and adventurous, though clearly written for younger readers.',
4.3,NULL,NULL,NULL);