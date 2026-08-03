import json

# Comprehensive traditional Christian original hymns present in the 1985 LDS Hymnal
ORIGINAL_HYMNS = [
    {
        "title": "Joy to the World",
        "lds_hymn_number": 201,
        "original_author": "Isaac Watts",
        "publication_year": 1719,
        "original_source": "Psalms of David Imitated in the Language of the New Testament",
        "lyrics": """Verse 1: Joy to the world, the Lord is come! Let earth receive her King; Let ev'ry heart prepare him room, And heav'n and nature sing, And heav'n and nature sing, And heav'n, and heav'n and nature sing.
Verse 2: Joy to the earth, the Savior reigns! Let men their songs employ; While fields and floods, rocks, hills, and plains Repeat the sounding joy, Repeat the sounding joy, Repeat, repeat the sounding joy.
Verse 3: No more let sins and sorrows grow, Nor thorns infest the ground; He comes to make his blessings flow Far as the curse is found, Far as the curse is found, Far as, far as the curse is found.
Verse 4: He rules the world with truth and grace, And makes the nations prove The glories of his righteousness, And wonders of his love, And wonders of his love, And wonders, wonders of his love.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "title": "How Firm a Foundation",
        "lds_hymn_number": 85,
        "original_author": "Rippon's Selection (signed 'K.')",
        "publication_year": 1787,
        "original_source": "A Selection of Hymns from the Best Authors",
        "lyrics": """Verse 1: How firm a foundation, ye saints of the Lord, Is laid for your faith in his excellent word! What more can he say than to you he hath said, Who unto the Savior for refuge have fled?
Verse 2: In ev'ry condition—in sickness, in health, In poverty's vale, or abounding in wealth, At home and abroad, on the land, on the sea, As thy days may demand, so thy succor shall be.
Verse 3: Fear not, I am with thee; oh be not dismayed, For I am thy God and will still give thee aid. I'll strengthen thee, help thee, and cause thee to stand, Upheld by my righteous, omnipotent hand.
Verse 4: When through the deep waters I call thee to go, The rivers of sorrow shall not overflow; For I will be with thee thy troubles to bless, And sanctify to thee thy deepest distress.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Redeemer of Israel",
        "lds_hymn_number": 6,
        "original_author": "Joseph Swain (adapted by W. W. Phelps)",
        "publication_year": 1791,
        "original_source": "Experimental Hymns ('O Thou in Whose Presence')",
        "lyrics": """Verse 1: O thou in whose presence my soul takes delight, On whom in affliction I call, My comfort by day and my song in the night, My hope, my salvation, my all!
Verse 2: Where dost thou at noontide resort with thy sheep, To feed them in pastures of love? Say, why in the valley of death should I weep, Or alone in the wilderness rove?
Verse 3: O why should I wander an alien from thee, Or cry in the desert for bread? Thy foes will rejoice when my sorrows they see, And smile at the tears I have shed.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Restoration"
    },
    {
        "title": "Abide with Me!",
        "lds_hymn_number": 166,
        "original_author": "Henry Francis Lyte",
        "publication_year": 1847,
        "original_source": "Remains of the Rev. H. F. Lyte",
        "lyrics": """Verse 1: Abide with me: fast falls the eventide; The darkness deepens; Lord, with me abide. When other helpers fail and comforts flee, Help of the helpless, O abide with me.
Verse 2: Swift to its close ebbs out life's little day; Earth's joys grow dim, its glories pass away; Change and decay in all around I see; O thou who changest not, abide with me.
Verse 3: I need thy presence every passing hour. What but thy grace can foil the tempter's power? Who like thyself my guide and stay can be? Through cloud and sunshine, O abide with me.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Sacrament"
    },
    {
        "title": "All People That on Earth Do Dwell",
        "lds_hymn_number": 249,
        "original_author": "William Kethe",
        "publication_year": 1561,
        "original_source": "Anglo-Genevan Psalter (Old 100th)",
        "lyrics": """Verse 1: All people that on earth do dwell, Sing to the Lord with cheerful voice. Him serve with fear, his praise forthtell; Come ye before him and rejoice.
Verse 2: The Lord, ye know, is God indeed; Without our aid he did us make. We are his folk, he doth us feed, And for his sheep he doth us take.
Verse 3: O enter then his gates with praise; Approach with joy his courts unto. Praise, laud, and bless his name always, For it is seemly so to do.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Come, Thou Fount of Every Blessing",
        "lds_hymn_number": 88,
        "original_author": "Robert Robinson",
        "publication_year": 1758,
        "original_source": "A Collection of Hymns for the Use of the Church of Christ",
        "lyrics": """Verse 1: Come, thou Fount of every blessing, Tune my heart to sing thy grace; Streams of mercy, never ceasing, Call for songs of loudest praise. Teach me some melodious sonnet, Sung by flaming tongues above. Praise the mount! I'm fixed upon it, Mount of thy redeeming love.
Verse 2: Here I raise my Ebenezer; Hither by thy help I'm come; And I hope, by thy good pleasure, Safely to arrive at home. Jesus sought me when a stranger, Wandering from the fold of God; He, to rescue me from danger, Interposed his precious blood.
Verse 3: O to grace how great a debtor Daily I'm constrained to be! Let thy goodness, like a fetter, Bind my wandering heart to thee. Prone to wander, Lord, I feel it, Prone to leave the God I love; Here's my heart, O take and seal it, Seal it for thy courts above.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Hark! The Herald Angels Sing",
        "lds_hymn_number": 209,
        "original_author": "Charles Wesley (altered by George Whitefield)",
        "publication_year": 1739,
        "original_source": "Hymns and Sacred Poems ('Hark, how all the welkin rings')",
        "lyrics": """Verse 1: Hark! The herald angels sing, \"Glory to the newborn King; Peace on earth, and mercy mild, God and sinners reconciled!\" Joyful, all ye nations, rise, Join the triumph of the skies; With th'angelic host proclaim, \"Christ is born in Bethlehem!\"
Refrain: Hark! The herald angels sing, \"Glory to the newborn King!\"
Verse 2: Christ, by highest heav'n adored; Christ, the everlasting Lord! Late in time behold him come, Offspring of the Virgin's womb. Veiled in flesh the Godhead see; Hail th'incarnate Deity, Pleased as man with men to dwell, Jesus, our Emmanuel.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "title": "Oh, Come, All Ye Faithful",
        "lds_hymn_number": 202,
        "original_author": "John Francis Wade (transl. Frederick Oakeley)",
        "publication_year": 1743,
        "original_source": "Adeste Fideles",
        "lyrics": """Verse 1: Oh, come, all ye faithful, joyful and triumphant! Oh, come ye, oh come ye to Bethlehem. Come and behold him, born the King of angels!
Refrain: Oh, come, let us adore him; Oh, come, let us adore him; Oh, come, let us adore him, Christ the Lord!
Verse 2: Sing, choirs of angels, sing in exultation; Sing, all ye citizens of heav'n above! Glory to God, glory in the highest!""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "title": "Silent Night",
        "lds_hymn_number": 204,
        "original_author": "Joseph Mohr (transl. John Freeman Young)",
        "publication_year": 1818,
        "original_source": "Stille Nacht, heilige Nacht",
        "lyrics": """Verse 1: Silent night, holy night, All is calm, all is bright Round yon virgin mother and child. Holy Infant, so tender and mild, Sleep in heavenly peace, Sleep in heavenly peace.
Verse 2: Silent night, holy night, Shepherds quake at the sight; Glories stream from heaven afar, Heav'nly hosts sing Alleluia! Christ the Savior is born, Christ the Savior is born.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Easter/Christmas"
    },
    {
        "title": "A Mighty Fortress Is Our God",
        "lds_hymn_number": 68,
        "original_author": "Martin Luther (transl. Frederick H. Hedge)",
        "publication_year": 1529,
        "original_source": "Geistliche Lieder ('Ein feste Burg ist unser Gott')",
        "lyrics": """Verse 1: A mighty fortress is our God, A bulwark never failing; Our helper he amid the flood Of mortal ills prevailing. For still our ancient foe Doth seek to work us woe; His craft and power are great, And armed with cruel hate, On earth is not his equal.
Verse 2: Did we in our own strength confide, Our striving would be losing, Were not the right man on our side, The man of God's own choosing. Dost ask who that may be? Christ Jesus, it is he; Lord Sabaoth his name, From age to age the same, And he must win the battle.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "God Moves in a Mysterious Way",
        "lds_hymn_number": 285,
        "original_author": "William Cowper",
        "publication_year": 1774,
        "original_source": "Olney Hymns ('Light Shining out of Darkness')",
        "lyrics": """Verse 1: God moves in a mysterious way His wonders to perform; He plants his footsteps in the sea And rides upon the storm.
Verse 2: Deep in unfathomable mines Of never-failing skill He treasures up his bright designs And works his sovereign will.
Verse 3: Ye fearful saints, fresh courage take; The clouds ye so much dread Are big with mercy and shall break In blessings on your head.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "For the Beauty of the Earth",
        "lds_hymn_number": 284,
        "original_author": "Folliott S. Pierpoint",
        "publication_year": 1864,
        "original_source": "Lyra Eucharistica",
        "lyrics": """Verse 1: For the beauty of the earth, For the glory of the skies, For the love which from our birth Over and around us lies:
Refrain: Lord of all, to thee we raise This our hymn of grateful praise.
Verse 2: For the beauty of each hour Of the day and of the night, Hill and vale, and tree and flower, Sun and moon, and stars of light:""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Guide Us, O Thou Great Jehovah",
        "lds_hymn_number": 83,
        "original_author": "William Williams (transl. Peter Williams)",
        "publication_year": 1745,
        "original_source": "Arglwydd, arwain trwy’r anialwch",
        "lyrics": """Verse 1: Guide me, O thou great Jehovah, Pilgrim through this barren land; I am weak, but thou art mighty; Hold me with thy powerful hand. Bread of heaven, bread of heaven, Feed me till I want no more; Feed me till I want no more.
Verse 2: Open now the crystal fountain, Whence the healing stream doth flow; Let the fire and cloudy pillar Lead me all my journey through. Strong Deliverer, strong Deliverer, Be thou still my strength and shield; Be thou still my strength and shield.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Now Thank We All Our God",
        "lds_hymn_number": 95,
        "original_author": "Martin Rinkart (transl. Catherine Winkworth)",
        "publication_year": 1636,
        "original_source": "Jesu Herz-Büchlein ('Nun danket alle Gott')",
        "lyrics": """Verse 1: Now thank we all our God With hearts and hands and voices, Who wondrous things hath done, In whom his world rejoices; Who from our mothers' arms Hath blessed us on our way With countless gifts of love, And still is ours today.
Verse 2: O may this bounteous God Through all our life be near us, With ever joyful hearts And blessed peace to cheer us; And keep us in his grace, And guide us when perplexed, And free us from all ills In this world and the next.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    },
    {
        "title": "Praise God, from Whom All Blessings Flow",
        "lds_hymn_number": 242,
        "original_author": "Thomas Ken",
        "publication_year": 1674,
        "original_source": "A Manual of Prayers for the Use of the Scholars of Winchester College",
        "lyrics": """Praise God, from whom all blessings flow; Praise him, all creatures here below; Praise him above, ye heav'nly host; Praise Father, Son, and Holy Ghost. Amen.""",
        "major_theme": "Taken from Christianity",
        "minor_theme": "Praise and Thanksgiving"
    }
]

def build():
    print(f"Saving {len(ORIGINAL_HYMNS)} traditional Christian original precursor hymns to JSON seeds...")
    with open("db/hymns_original_seed.json", "w", encoding="utf-8") as f:
        json.dump(ORIGINAL_HYMNS, f, indent=2, ensure_ascii=False)
    with open("backend/hymns_original_seed.json", "w", encoding="utf-8") as f:
        json.dump(ORIGINAL_HYMNS, f, indent=2, ensure_ascii=False)
    print("Saved db/hymns_original_seed.json and backend/hymns_original_seed.json successfully!")

if __name__ == "__main__":
    build()
