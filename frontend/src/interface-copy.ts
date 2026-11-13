export type Language = 'el' | 'en'

export const interfaceCopy = {
  el: {
    tag: 'ΚΛΙΝΙΚΕΣ ΜΕΛΕΤΕΣ · ΕΛΛΑΔΑ',
    skip: 'Μετάβαση στο περιεχόμενο',
    title: 'Πληροφορίες για κλινικές μελέτες',
    intro: 'Μια πρώτη ματιά σε πληροφορίες από το δημόσιο μητρώο ClinicalTrials.gov.',
    notice:
      'Το εργαλείο παρέχει πληροφορίες, όχι ιατρικές συμβουλές. Συζητήστε με τον γιατρό σας πριν πάρετε αποφάσεις για τη φροντίδα σας.',
    eyebrow: 'ΠΑΡΑΔΕΙΓΜΑ ΜΕΛΕΤΗΣ',
    example:
      'Αυτή είναι μία πραγματική καταχώριση, όχι αποτέλεσμα αναζήτησης ή σύσταση συμμετοχής.',
    loading: 'Φόρτωση από το ClinicalTrials.gov…',
    error: 'Δεν ήταν δυνατή η φόρτωση της μελέτης. Δοκιμάστε ξανά αργότερα.',
    retry: 'Προσπαθήστε ξανά',
    status: 'Κατάσταση μελέτης',
    completed: 'Ολοκληρωμένη',
    missing: 'Δεν αναφέρεται',
    updated: 'Τελευταία ενημέρωση μητρώου',
    about: 'Σύνοψη από το μητρώο',
    original: 'Ο τίτλος και η σύνοψη παρατίθενται στην αρχική τους γλώσσα.',
    locations: 'Τοποθεσίες στην Ελλάδα',
    noLocations: 'Δεν υπάρχει επιβεβαιωμένη τοποθεσία στην Ελλάδα στην τρέχουσα καταχώριση.',
    source: 'Δείτε την αρχική καταχώριση',
    caveat:
      'Οι πληροφορίες μπορεί να έχουν αλλάξει. Ελέγξτε την ημερομηνία ενημέρωσης και επικοινωνήστε με την ερευνητική ομάδα.',
    scope:
      'Τα κριτήρια συμμετοχής εμφανίζονται όπως καταχωρίστηκαν. Οι απλές εξηγήσεις τους δεν είναι ακόμη διαθέσιμες.',
    participation: 'Ποιοι μπορούν να συμμετάσχουν;',
    participationIntro:
      'Οι ερευνητές ορίζουν προϋποθέσεις συμμετοχής και λόγους αποκλεισμού. Τα πεδία μπορεί να διαφέρουν από το κείμενο. Συζητήστε τυχόν διαφορές με την ερευνητική ομάδα, που μπορεί να επιβεβαιώσει αν μπορείτε να συμμετάσχετε.',
    minAge: 'Ελάχιστη ηλικία',
    maxAge: 'Μέγιστη ηλικία',
    sexEligibility: 'Βιολογικό φύλο στο μητρώο',
    sexAll: 'Όλα τα φύλα',
    sexFemale: 'Γυναίκες',
    sexMale: 'Άνδρες',
    healthyVolunteers: 'Δέχεται υγιείς εθελοντές',
    genderBased: 'Κριτήρια με βάση το κοινωνικό φύλο',
    genderDescription: 'Περιγραφή κριτηρίων κοινωνικού φύλου',
    yes: 'Ναι',
    no: 'Όχι',
    criteriaOriginal: 'Κείμενο κριτηρίων από το μητρώο',
    criteriaNote:
      'Το κείμενο εμφανίζεται όπως καταχωρίστηκε, συνήθως στα αγγλικά, και μπορεί να περιέχει ιατρικούς όρους. Μπορεί να μην περιλαμβάνει όλες τις προϋποθέσεις και τους λόγους αποκλεισμού.',
    criteriaMissing: 'Το μητρώο δεν παρέχει κείμενο κριτηρίων.',
    criteriaSource: 'Πηγή: αρχική καταχώριση, ενότητα Participation Criteria',
    statusSource: 'Πηγή κατάστασης',
    datesSource: 'Πηγή ημερομηνίας',
    summarySource: 'Πηγή σύνοψης: Study Overview',
    locationsSource: 'Πηγή τοποθεσιών: Contacts and Locations',
    searchTitle: 'Αναζητήστε μελέτες στην Ελλάδα',
    euTitle: 'Ευρωπαϊκές μελέτες στην Ελλάδα',
    euIntro:
      'Αναζητήστε στοιχεία από το ευρωπαϊκό μητρώο CTIS. Η αναζήτηση δεν ελέγχει αν μπορείτε να συμμετάσχετε.',
    euLookupTitle: 'Αναζήτηση με ευρωπαϊκό αριθμό',
    euSearchTitle: 'Αναζήτηση με πάθηση',
    euSearchIntro:
      'Αναζητήστε με αγγλικό όρο ή επιλέξτε μία από τις λίγες διαθέσιμες προτάσεις για ελληνικό κείμενο.',
    euSearchPrivacy:
      'Ο όρος αποστέλλεται στο ευρωπαϊκό μητρώο CTIS. Μην συμπεριλάβετε όνομα, στοιχεία επικοινωνίας ή άλλα στοιχεία που σας ταυτοποιούν.',
    euSearchNote:
      'Πιθανώς σχετικές καταχωρίσεις με την Ελλάδα στις χώρες της μελέτης, όχι έλεγχος καταλληλότητας. Ο τίτλος και η πάθηση εμφανίζονται όπως παρέχονται από το μητρώο, συνήθως στα αγγλικά. Ελέγξτε στην καταχώριση την κατάσταση κάθε κέντρου.',
    euSubtypeCaution:
      'Ο μικροκυτταρικός και ο μη μικροκυτταρικός καρκίνος του πνεύμονα είναι διαφορετικοί τύποι. Το CTIS μπορεί να εμφανίσει και τους δύο. Ο έλεγχος επισημαίνει μόνο ορισμένες αναφορές· άλλες διαφορές ενδέχεται να μην επισημαίνονται. Ελέγξτε κάθε καταχώριση με τον γιατρό σας.',
    euSubtypeSource: 'Πηγή για τους τύπους καρκίνου του πνεύμονα',
    euSubtypeNotice:
      'Ο τίτλος ή η πάθηση στο μητρώο αναφέρει «non-small cell» (μη μικροκυτταρικός). Ελέγξτε αν η μελέτη είναι σχετική. Αυτή η ένδειξη δεν κρίνει αν μπορείτε να συμμετάσχετε.',
    euTotal: 'Αποτελέσματα στο CTIS',
    euEmpty: 'Δεν βρέθηκαν αποτελέσματα. Αυτό δεν αποδεικνύει ότι δεν υπάρχει σχετική μελέτη.',
    euViewCriteria: 'Προβολή κύριων κριτηρίων',
    euMoreBusy:
      'Το ευρωπαϊκό μητρώο είναι απασχολημένο. Τα προηγούμενα αποτελέσματα παραμένουν διαθέσιμα.',
    euNumber: 'Ευρωπαϊκός αριθμός μελέτης',
    euExample: '2025-522873-12-00',
    euButton: 'Εύρεση μελέτης',
    euHelp: 'Εισαγάγετε τον αριθμό EUCT που αναφέρεται στην ευρωπαϊκή καταχώριση.',
    euInvalid: 'Εισαγάγετε αριθμό με τη μορφή 2025-522873-12-00.',
    euNotFound:
      'Δεν βρέθηκε μελέτη με αυτόν τον αριθμό που να αναφέρει την Ελλάδα. Ελέγξτε την αρχική καταχώριση στο CTIS.',
    euBusy: 'Το ευρωπαϊκό μητρώο είναι απασχολημένο. Δοκιμάστε ξανά αργότερα.',
    euError: 'Δεν ήταν δυνατή η φόρτωση από το ευρωπαϊκό μητρώο. Δοκιμάστε ξανά αργότερα.',
    euCountry:
      'Η Ελλάδα αναφέρεται στη μελέτη. Ελέγξτε στην αρχική καταχώριση αν κάποιο κέντρο αναζητά συμμετέχοντες.',
    euObjective: 'Κύριος στόχος της μελέτης',
    euObjectiveIntro:
      'Το κείμενο εμφανίζεται όπως καταχωρίστηκε στο CTIS και μπορεί να περιέχει ιατρικούς όρους.',
    euObjectiveMissing:
      'Δεν βρέθηκε κύριος στόχος στα ελληνικά ή στα αγγλικά στα δεδομένα που ελέγχθηκαν. Δείτε την αρχική καταχώριση για άλλες γλώσσες.',
    euObjectiveSource:
      'Πηγή: CTIS → Full trial information → Main objective (English / additional languages)',
    euEnglishMissing: 'Δεν βρέθηκε αγγλικό κείμενο στα δεδομένα που ελέγχθηκαν',
    euCriteriaNote:
      'Αυτά είναι τα κύρια κριτήρια όπως καταχωρίστηκαν, όχι έλεγχος καταλληλότητας. Μπορεί να υπάρχουν και άλλα. Συζητήστε τα με τον γιατρό και την ερευνητική ομάδα.',
    euInclusion: 'Κύρια κριτήρια συμμετοχής',
    euExclusion: 'Κύρια κριτήρια αποκλεισμού',
    euGreekMissing: 'Δεν βρέθηκε ελληνική μετάφραση στα δεδομένα που ελέγχθηκαν',
    euCriteriaMissing:
      'Δεν δόθηκαν κύρια κριτήρια σε αυτά τα δεδομένα. Ελέγξτε την αρχική καταχώριση.',
    euSource: 'Δείτε την ευρωπαϊκή καταχώριση στο CTIS',
    searchIntro:
      'Αναζητήστε μια πάθηση στο ClinicalTrials.gov με αγγλικό όρο. Για λίγες παθήσεις αναγνωρίζουμε και απλές ελληνικές φράσεις, όπως «Έχω διαβήτη τύπου 2».',
    condition: 'Πάθηση ή απλή φράση',
    suggestedTerm: 'Προτεινόμενος αγγλικός όρος:',
    chosenFrom: 'Ο όρος επιλέχθηκε για:',
    suggestionLimit:
      'Ελέγξτε αν ο όρος εκφράζει αυτό που θέλετε να αναζητήσετε. Δεν αποτελεί διάγνωση ή έλεγχο καταλληλότητας.',
    termSource: 'Πηγή του όρου',
    useTerm: 'Χρήση του αγγλικού όρου',
    greekUnsupported:
      'Δεν αναγνωρίζουμε αυτό το ελληνικό κείμενο. Χρησιμοποιήστε αγγλικό όρο ή δοκιμάστε τον ευρωπαϊκό χάρτη παρακάτω.',
    greekHelp:
      'Αναγνωρίζονται μόνο λίγα ονόματα παθήσεων και ορισμένες φράσεις που αρχίζουν με «έχω». Δεν αναγνωρίζονται αρνήσεις ή πρόσθετες λεπτομέρειες.',
    mapIntro: 'Για αναζήτηση στα ελληνικά μπορείτε επίσης να επισκεφθείτε τον',
    mapLink: 'ευρωπαϊκό χάρτη κλινικών μελετών του EMA',
    mapPrivacy: 'σε ξεχωριστή σελίδα. Θα χρειαστεί να πληκτρολογήσετε ξανά την αναζήτησή σας.',
    privacy:
      'Ο όρος αναζήτησης αποστέλλεται στο ClinicalTrials.gov. Μην συμπεριλάβετε όνομα, στοιχεία επικοινωνίας ή άλλες πληροφορίες που σας ταυτοποιούν.',
    searchButton: 'Αναζήτηση μελετών',
    openOnly: 'Μόνο μελέτες που αναζητούν ή θα αναζητήσουν συμμετέχοντες',
    filterHelp:
      'Το φίλτρο αφορά τη συνολική κατάσταση της μελέτης. Ένα κέντρο στην Ελλάδα μπορεί να έχει διαφορετική κατάσταση.',
    searching: 'Αναζήτηση…',
    results: 'Αποτελέσματα αναζήτησης',
    resultsFor: 'Αποτελέσματα για',
    resultsFiltered: 'Φίλτρο συνολικής κατάστασης ενεργό',
    resultsNote:
      'Πιθανώς σχετικές καταχωρίσεις, όχι έλεγχος καταλληλότητας. Η κατάσταση της μελέτης αφορά τη μελέτη συνολικά και μπορεί να διαφέρει ανά κέντρο.',
    empty:
      'Δεν βρέθηκε καταχώριση με τοποθεσία στην Ελλάδα στα αποτελέσματα που ελέγχθηκαν. Δοκιμάστε άλλον αγγλικό όρο.',
    moreResults: 'Υπάρχουν περισσότερα αποτελέσματα από το μητρώο.',
    loadMore: 'Φόρτωση περισσότερων μελετών',
    loadingMore: 'Φόρτωση περισσότερων μελετών…',
    moreError:
      'Δεν ήταν δυνατή η φόρτωση περισσότερων μελετών. Τα προηγούμενα αποτελέσματα παραμένουν διαθέσιμα.',
    searchError: 'Η αναζήτηση δεν ήταν δυνατή. Δοκιμάστε ξανά αργότερα.',
    registryBusy: 'Η σύνδεση με το μητρώο είναι απασχολημένη. Περιμένετε και προσπαθήστε ξανά.',
    moreBusy:
      'Η σύνδεση με το μητρώο είναι απασχολημένη. Τα προηγούμενα αποτελέσματα παραμένουν διαθέσιμα. Περιμένετε και προσπαθήστε ξανά.',
    siteStatus: 'Κατάσταση κέντρου',
    recruiting: 'Προσέλκυση συμμετεχόντων',
    notYetRecruiting: 'Δεν έχει ξεκινήσει η προσέλκυση',
    activeNotRecruiting: 'Σε εξέλιξη, χωρίς προσέλκυση',
    invitation: 'Μόνο με πρόσκληση',
    suspended: 'Σε αναστολή',
    terminated: 'Τερματίστηκε πρόωρα',
    withdrawn: 'Αποσύρθηκε',
    unknown: 'Άγνωστη',
  },
  en: {
    tag: 'CLINICAL STUDIES · GREECE',
    skip: 'Skip to content',
    title: 'Information about clinical studies',
    intro: 'A first look at information from the public ClinicalTrials.gov registry.',
    notice:
      'This tool provides information, not medical advice. Talk to your doctor before making decisions about your care.',
    eyebrow: 'EXAMPLE STUDY',
    example:
      'This is a real registry record, not a search result or a recommendation to participate.',
    loading: 'Loading from ClinicalTrials.gov…',
    error: 'The study could not be loaded. Please try again later.',
    retry: 'Try again',
    status: 'Study status',
    completed: 'Completed',
    missing: 'Not reported',
    updated: 'Registry last updated',
    about: 'Summary from the registry',
    original: 'The title and summary are shown in their original language.',
    locations: 'Locations in Greece',
    noLocations: 'No location in Greece is confirmed in the current record.',
    source: 'View the original record',
    caveat: 'Information may have changed. Check the update date and contact the study team.',
    scope:
      'Participation criteria are shown as registered. Plain-language explanations are not yet available.',
    participation: 'Who can take part?',
    participationIntro:
      'Researchers set requirements for joining and reasons for exclusion. The fields can differ from the written criteria. Discuss any differences with the study team, who can confirm whether you can participate.',
    minAge: 'Minimum age',
    maxAge: 'Maximum age',
    sexEligibility: 'Sex listed in the registry',
    sexAll: 'All sexes',
    sexFemale: 'Female',
    sexMale: 'Male',
    healthyVolunteers: 'Accepts healthy volunteers',
    genderBased: 'Gender-based eligibility',
    genderDescription: 'Gender eligibility description',
    yes: 'Yes',
    no: 'No',
    criteriaOriginal: 'Criteria text from the registry',
    criteriaNote:
      'The text is shown as registered, usually in English, and may contain medical terms. It may not include every requirement or reason for exclusion.',
    criteriaMissing: 'The registry does not provide criteria text.',
    criteriaSource: 'Source: original record, Participation Criteria section',
    statusSource: 'Source for status',
    datesSource: 'Source for date',
    summarySource: 'Source for summary: Study Overview',
    locationsSource: 'Source for locations: Contacts and Locations',
    searchTitle: 'Search studies in Greece',
    euTitle: 'European studies in Greece',
    euIntro: 'Search the European CTIS registry. This is not an eligibility check.',
    euLookupTitle: 'Look up by European trial number',
    euSearchTitle: 'Search by condition',
    euSearchIntro:
      'Search with an English term or choose one of the limited suggestions for Greek text.',
    euSearchPrivacy:
      'The search term is sent to the European CTIS registry. Do not include your name, contact details, or other identifying information.',
    euSearchNote:
      'Potentially relevant records listing Greece among their countries, not an eligibility check. Titles and conditions are shown as provided by the registry, usually in English. Check the record for the status of each site.',
    euSubtypeCaution:
      'Small-cell and non-small-cell lung cancer are different types. CTIS may return both. This check flags only some text. Other differences may not be flagged. Check each record with your doctor.',
    euSubtypeSource: 'Source for lung cancer types',
    euSubtypeNotice:
      'The registry title or condition mentions non-small cell. Check whether this trial is relevant. This flag does not decide whether you can take part.',
    euTotal: 'CTIS results',
    euEmpty: 'No results were found. This does not prove that no relevant study exists.',
    euViewCriteria: 'View main criteria',
    euMoreBusy: 'The European registry is busy. Previous results remain available.',
    euNumber: 'European trial number',
    euExample: '2025-522873-12-00',
    euButton: 'Find study',
    euHelp: 'Enter the EUCT number shown in the European record.',
    euInvalid: 'Enter a number in the format 2025-522873-12-00.',
    euNotFound:
      'No study with that number was found listing Greece. Check the original record in CTIS.',
    euBusy: 'The European registry is busy. Please try again later.',
    euError:
      'The European registry could not be reached or its data could not be read. Please try again later.',
    euCountry:
      'Greece is listed in this study. Check the original record to see whether a site is recruiting.',
    euObjective: 'Main objective of the study',
    euObjectiveIntro: 'This text is shown as recorded in CTIS and may contain medical terms.',
    euObjectiveMissing:
      'No main objective in Greek or English was found in the data checked. See the original record for other languages.',
    euObjectiveSource:
      'Source: CTIS → Full trial information → Main objective (English / additional languages)',
    euEnglishMissing: 'English text was not found in the data checked',
    euCriteriaNote:
      'These are the main criteria as registered, not an eligibility check. There may be others. Discuss them with your doctor and the study team.',
    euInclusion: 'Main inclusion criteria',
    euExclusion: 'Main exclusion criteria',
    euGreekMissing: 'Greek translation was not found in the data checked',
    euCriteriaMissing: 'No main criteria were provided in these data. Check the original record.',
    euSource: 'View the European record in CTIS',
    searchIntro:
      'Search ClinicalTrials.gov using an English condition term. For a few conditions we also recognize simple Greek phrases, such as “Έχω διαβήτη τύπου 2”.',
    condition: 'Condition or simple phrase',
    suggestedTerm: 'Suggested English term:',
    chosenFrom: 'Term selected for:',
    suggestionLimit:
      'Check that this term describes what you want to search for. It is not a diagnosis or an eligibility check.',
    termSource: 'Source for this term',
    useTerm: 'Use the English term',
    greekUnsupported:
      'We do not recognize this Greek text. Use an English term or try the European trial map below.',
    greekHelp:
      'Only a few condition names and some phrases starting with “έχω” are recognized. Negatives and extra details are not recognized.',
    mapIntro: 'To search in Greek, you can also visit the',
    mapLink: 'EMA European clinical trials map',
    mapPrivacy: 'on a separate page. You will need to enter your search again.',
    privacy:
      'The search term is sent to ClinicalTrials.gov. Do not include your name, contact details, or other identifying information.',
    searchButton: 'Search studies',
    openOnly: 'Only studies recruiting or not yet recruiting',
    filterHelp:
      'This filter uses the overall study status. A site in Greece may have a different status.',
    searching: 'Searching…',
    results: 'Search results',
    resultsFor: 'Results for',
    resultsFiltered: 'Overall recruitment filter applied',
    resultsNote:
      'Potentially relevant records, not an eligibility check. The study status is for the overall study and may differ by location.',
    empty:
      'No record with a location in Greece was found among the results checked. Try another English term.',
    moreResults: 'More results are available from the registry.',
    loadMore: 'Load more studies',
    loadingMore: 'Loading more studies…',
    moreError: 'More studies could not be loaded. Previous results are still available.',
    searchError: 'The search could not be completed. Please try again later.',
    registryBusy: 'The registry connection is busy. Please wait and try again.',
    moreBusy:
      'The registry connection is busy. Previous results are still available. Please wait and try again.',
    siteStatus: 'Site status',
    recruiting: 'Recruiting',
    notYetRecruiting: 'Not yet recruiting',
    activeNotRecruiting: 'Active, not recruiting',
    invitation: 'Enrolling by invitation',
    suspended: 'Suspended',
    terminated: 'Terminated',
    withdrawn: 'Withdrawn',
    unknown: 'Unknown',
  },
}

export type InterfaceCopy = (typeof interfaceCopy)[Language]
