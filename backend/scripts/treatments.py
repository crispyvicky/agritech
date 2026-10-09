"""Treatment tips for PlantDoc disease / leaf classes."""

TREATMENTS = {
    "Apple leaf": "Healthy apple foliage. Keep good air flow, avoid overwatering leaves, and monitor weekly for spots.",
    "Apple rust leaf": "Remove nearby juniper hosts if possible. Apply a fungicide labeled for apple rust at bud break; rake and destroy fallen leaves.",
    "Apple Scab Leaf": "Prune for airflow, remove fallen leaves, and use a scab fungicide in early spring before wet weather.",
    "Bell_pepper leaf": "Healthy pepper leaf. Water at the soil line, mulch, and watch for dark spots after rain.",
    "Bell_pepper leaf spot": "Avoid overhead irrigation. Remove infected leaves; use copper-based spray if spread continues.",
    "Blueberry leaf": "Healthy blueberry leaf. Maintain acidic soil (pH ~4.5–5.5) and even moisture.",
    "Cherry leaf": "Healthy cherry leaf. Prune crowded branches and keep leaves dry when possible.",
    "Corn Gray leaf spot": "Use resistant hybrids if available, rotate crops, and apply fungicide at early lesion stage in humid weather.",
    "Corn leaf blight": "Rotate away from corn, bury residue, and consider fungicide at first lesions during warm, wet periods.",
    "Corn rust leaf": "Plant resistant varieties; fungicide can help if rust appears early on susceptible corn.",
    "grape leaf": "Healthy grape leaf. Train vines for sunlight and airflow; remove suckers.",
    "grape leaf black rot": "Remove mummified berries and infected leaves. Use fungicide from bloom through fruit set in wet seasons.",
    "Peach leaf": "Healthy peach leaf. Thin fruit and prune for open canopy to reduce humidity.",
    "Potato leaf early blight": "Mulch, avoid wetting leaves, rotate crops; fungicide at first target-like spots.",
    "Potato leaf late blight": "Act fast: remove infected plants, avoid leaf wetness, and use a late-blight fungicide. Do not compost infected material.",
    "Raspberry leaf": "Healthy raspberry leaf. Thin canes for airflow and water at the base.",
    "Soyabean leaf": "Healthy soybean leaf. Maintain fertility and watch for sudden yellowing or spots.",
    "Squash Powdery mildew leaf": "Improve airflow, water soil not leaves; apply sulfur or potassium bicarbonate sprays early.",
    "Strawberry leaf": "Healthy strawberry leaf. Renew beds, mulch, and remove old leaves after harvest.",
    "Tomato Early blight leaf": "Mulch, stake plants, remove lower infected leaves; fungicide with chlorothalonil/copper as labeled.",
    "Tomato leaf": "Healthy tomato leaf. Stake/cage plants and water at the base in the morning.",
    "Tomato leaf bacterial spot": "Avoid working wet plants; remove infected leaves; copper sprays may slow spread. Use clean seed next season.",
    "Tomato leaf late blight": "Remove and destroy infected plants quickly. Keep foliage dry; apply late-blight fungicide. Rotate next year.",
    "Tomato leaf mosaic virus": "No chemical cure. Remove infected plants, control aphids, and disinfect tools. Use resistant varieties next season.",
    "Tomato leaf yellow virus": "Control whiteflies; remove infected plants. Use resistant cultivars and reflective mulch if available.",
    "Tomato mold leaf": "Improve airflow, reduce humidity, remove affected leaves; fungicide for leaf mold if needed in greenhouses.",
    "Tomato Septoria leaf spot": "Remove lower leaves, mulch soil, avoid splash; fungicide early if spots spread upward.",
}


def treatment_for(label: str) -> str:
    return TREATMENTS.get(
        label,
        "Follow good sanitation: remove badly damaged leaves, improve airflow, and avoid wetting foliage. Confirm with a local agronomist if unsure.",
    )
