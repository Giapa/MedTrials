type ConditionTerm = {
  greek: string[]
  english: string
  sourceUrl: string
}

const terms: ConditionTerm[] = [
  {
    greek: ['καρκίνος μαστού', 'καρκίνος του μαστού', 'καρκίνο μαστού', 'καρκίνο του μαστού'],
    english: 'breast cancer',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/talzenna-epar-product-information_el.pdf',
  },
  {
    greek: [
      'διαβήτης τύπου 2',
      'διαβήτη τύπου 2',
      'διαβήτης τύπου δύο',
      'διαβήτη τύπου δύο',
      'σακχαρώδης διαβήτης τύπου 2',
    ],
    english: 'type 2 diabetes',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/ifirmasta-epar-product-information_el.pdf',
  },
  {
    greek: ['μικροκυτταρικός καρκίνος πνεύμονα', 'μικροκυτταρικός καρκίνος του πνεύμονα'],
    english: 'small cell lung cancer',
    sourceUrl:
      'https://www.ema.europa.eu/en/documents/orphan-designation/eu304255-public-summary-positive-opinion-orphan-designation-sabarubicin-treatment-small-cell-lung-cancer_en.pdf',
  },
  {
    greek: [
      'μη μικροκυτταρικός καρκίνος πνεύμονα',
      'μη μικροκυτταρικός καρκίνος του πνεύμονα',
      'μη-μικροκυτταρικός καρκίνος πνεύμονα',
      'μη-μικροκυτταρικός καρκίνος του πνεύμονα',
    ],
    english: 'non-small cell lung cancer',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/zirabev-epar-product-information_el.pdf',
  },
  {
    greek: ['σκληρόδερμα'],
    english: 'scleroderma',
    sourceUrl: 'https://www.orpha.net/pdfs/data/patho/Pro/el/Scleroderma_GR_el_PRO_ORPHA801.pdf',
  },
  {
    greek: ['διαβήτης', 'διαβήτη'],
    english: 'diabetes',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/ifirmasta-epar-product-information_el.pdf',
  },
  {
    greek: ['άσθμα'],
    english: 'asthma',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/aerivio-spiromax-epar-product-information_el.pdf',
  },
  {
    greek: ['σκλήρυνση κατά πλάκας'],
    english: 'multiple sclerosis',
    sourceUrl:
      'https://www.ema.europa.eu/el/documents/product-information/fampyra-epar-product-information_el.pdf',
  },
]

function normalize(value: string): string {
  return value.toLowerCase().normalize('NFD').replace(/\p{M}/gu, '').trim().replace(/\s+/g, ' ')
}

export function hasGreekText(value: string): boolean {
  return /\p{Script=Greek}/u.test(value)
}

export function findGreekConditionTerm(value: string): ConditionTerm | null {
  const input = normalize(value)
    .replace(/^εχω /, '')
    .replace(/\.$/, '')
    .trimEnd()
  return terms.find((term) => term.greek.some((name) => normalize(name) === input)) ?? null
}
