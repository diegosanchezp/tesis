import Alpine from "alpinejs"

import { startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"


// Register component
startAlpine({
    components: [],
    stores: [
        profileStore
    ]
})
