const carreraSelector = () => ({
    carreras_group: {
        "Ciencias": ["Computación", "Biología"],
        "Ingeniería": ["Ingeniería Eléctrica", "Ingeniería Civil"],
        "Arquitectura": ["Arquitectura y urbanismo", "Farmacia"]
    },
    carreras: [],
    search_key: "",

    get filteredCarreras() {
        let filtCarrerasGroup = {}
        for (const group of Object.keys(this.carreras_group)) {
            filtCarrerasGroup[group] = this.carreras_group[group].filter(
                i => {
                    if (this.search_key != ""){
                        // Perform case insensitive search
                        const regex = new RegExp(this.search_key, "i")
                        return i.match(regex)
                    }
                    return i
                }
            )
        }
        return filtCarrerasGroup
    }
})

export {carreraSelector}
