import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import {registerUrls} from "js/config/urls"
const select_carrera_def = () => ({

    // The selected from localstorage
    profile: Alpine.$persist("").as("profile"),

    carreer: Alpine.$persist('').as('carreer'),

    selected: false,

    get next_url(){
        if (this.profile === "mentor"){
            return registerUrls.add_exp
        }
        if (this.profile === "estudiante"){
            return registerUrls.select_specialization(this.carreer)

        }
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
