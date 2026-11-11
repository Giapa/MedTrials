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
    scope: 'Η αναζήτηση μελετών και οι απλές εξηγήσεις θα προστεθούν σε επόμενο στάδιο.',
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
    scope: 'Study search and plain-language explanations will be added in a later stage.',
  },
}

export type InterfaceCopy = (typeof interfaceCopy)[Language]
