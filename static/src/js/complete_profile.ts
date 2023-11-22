import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"

// Component definition
const complete_profile = (urlCarrer: string) => ({
    specializations: [],
    search_key: "",

    // The selected from localstorage
    profile: Alpine.$persist("").as("profile"),

    // The selected carrer from localstorage
    carreer: Alpine.$persist('').as('carreer'),

    // The selected specialization from localstorage
    specialization_storage: Alpine.$persist("").as("specialization"),

    // Compute selected specialization
    specialization: "",

    // The selected interest themes
    interests: Alpine.$persist<string[]>([]).as("themes"),

    // The carrer from the url path
    urlCarreer: urlCarrer,

    init(){
        console.log(this.interests)
        if(this.specialization_storage !== "No tengo especialización"){
            this.specialization = this.specialization_storage
        }
    },
})


const completeProfile: myAlpineComponent = {
    name: "complete_profile",
    component: complete_profile,
}

// Register component
startAlpine({
    components: [
        completeProfile
    ],
    stores: [
        profileStore
    ]
})
