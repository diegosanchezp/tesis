import Alpine from "alpinejs"
import htmx from 'htmx.org';

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"

document.addEventListener('alpine:initialized', () => {
    // Do some checkups
    const profileInput = (document.querySelector("input[name='profile']") as HTMLInputElement)

    if(!profileInput){
        console.debug("profile input not found")
    }

    const profile = profileInput.value

    if(!document.querySelector("input[name='carreer']")){
        console.debug("carreer input not found")
    }

    if(!profile){
        console.debug("profile input not found")
    }

    if(profile == "estudiante"){
    }

    if(profile == "mentor"){
        if(!localStorage.getItem("mentor_cleaned_data")){
            console.debug("mentor_cleaned_data is not set on localStorage")
        }
    }
})

document.addEventListener("DOMContentLoaded", () => {

})

// Component definition
const complete_profile = (urlCarrer: string, formsetPrefix: string) => ({
    specializations: [],
    search_key: "",

    mentor_exp: Alpine.$persist([]).as("mentor_cleaned_data"),

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
    formsetPrefix: formsetPrefix,

    errors: {},

    init(){
        console.debug(this.interests)
        console.debug(this.formsetPrefix)
        console.debug(this.mentor_exp.length)
        if(this.specialization_storage !== "No tengo especialización"){
            this.specialization = this.specialization_storage
        }
        // Do some checks
    },

    // Event listener for setting error messages
    set_form_errors(evt){
        this.errors = {
            entity_form: JSON.parse(evt.detail.entity_form),
            user_form: JSON.parse(evt.detail.user_form)
        }
        console.debug(this.errors)
    }
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
