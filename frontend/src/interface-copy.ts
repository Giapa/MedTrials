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
    scope: 'Οι απλές εξηγήσεις των κριτηρίων συμμετοχής δεν είναι ακόμη διαθέσιμες.',
    searchTitle: 'Αναζητήστε μελέτες στην Ελλάδα',
    searchIntro:
      'Αναζητήστε μια πάθηση στο ClinicalTrials.gov. Προς το παρόν χρησιμοποιήστε αγγλικούς όρους, όπως “breast cancer”.',
    condition: 'Πάθηση ή κατάσταση υγείας στα αγγλικά',
    privacy:
      'Ο όρος αναζήτησης αποστέλλεται στο ClinicalTrials.gov. Μην συμπεριλάβετε όνομα, στοιχεία επικοινωνίας ή άλλες πληροφορίες που σας ταυτοποιούν.',
    searchButton: 'Αναζήτηση μελετών',
    openOnly: 'Μόνο μελέτες που αναζητούν ή θα αναζητήσουν συμμετέχοντες',
    filterHelp:
      'Το φίλτρο αφορά τη συνολική κατάσταση της μελέτης. Ένα κέντρο στην Ελλάδα μπορεί να έχει διαφορετική κατάσταση.',
    searching: 'Αναζήτηση…',
    results: 'Αποτελέσματα αναζήτησης',
    resultsNote:
      'Πιθανώς σχετικές καταχωρίσεις, όχι έλεγχος καταλληλότητας. Η κατάσταση της μελέτης αφορά τη μελέτη συνολικά και μπορεί να διαφέρει ανά κέντρο.',
    empty:
      'Δεν βρέθηκε επιβεβαιωμένη τοποθεσία στην Ελλάδα στις πρώτες καταχωρίσεις που ελέγχθηκαν. Δοκιμάστε άλλον αγγλικό όρο.',
    moreResults:
      'Υπάρχουν περισσότερα αποτελέσματα. Εμφανίζονται έως οι πρώτες 10 καταχωρίσεις από το μητρώο.',
    searchError: 'Η αναζήτηση δεν ήταν δυνατή. Δοκιμάστε ξανά αργότερα.',
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
    scope: 'Plain-language explanations of participation criteria are not yet available.',
    searchTitle: 'Search studies in Greece',
    searchIntro:
      'Search ClinicalTrials.gov for a condition. For now, use English terms, such as “breast cancer”.',
    condition: 'Condition or health situation in English',
    privacy:
      'The search term is sent to ClinicalTrials.gov. Do not include your name, contact details, or other identifying information.',
    searchButton: 'Search studies',
    openOnly: 'Only studies recruiting or not yet recruiting',
    filterHelp:
      'This filter uses the overall study status. A site in Greece may have a different status.',
    searching: 'Searching…',
    results: 'Search results',
    resultsNote:
      'Potentially relevant records, not an eligibility check. The study status is for the overall study and may differ by location.',
    empty:
      'No confirmed location in Greece was found among the first records checked. Try another English term.',
    moreResults: 'More results are available. Up to the first 10 registry records are shown.',
    searchError: 'The search could not be completed. Please try again later.',
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
