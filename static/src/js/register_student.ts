import Alpine from "alpinejs"

import { startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"
import {carreraSelector} from "js/components/carrera_selector";


// Register component
startAlpine({
    components: [{
        name: "carrera_selector",
        component: carreraSelector,
    }],
    stores: [
        profileStore
    ]
})
