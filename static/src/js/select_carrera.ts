import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine } from "js/utils/alpine"

const select_carrera_def = () => ({
    carreer: Alpine.$persist('').as('carreer'),
    selected: false,

    get next_url(){
        return `/register/select_carreer_specialization/${this.carreer}`
    }
})

const select_carrera: myAlpineComponent = {
    name: "select_carrera",
    component: select_carrera_def,
}
// Register component
startAlpine({
    components: [
        select_carrera
    ],
    stores: [
    ]
})
