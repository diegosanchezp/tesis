import Alpine from "alpinejs"
import htmx from 'htmx.org';

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"

document.addEventListener('alpine:initialized', () => {
    // Do some checkups
    const profileInput = (document.querySelector("input[name='profile']") as HTMLInputElement)

    if(!profileInput){
        console.log("profile input not found")
    }

    const profile = profileInput.value

    if(!document.querySelector("input[name='carreer']")){
        console.log("carreer input not found")
    }

    if(!profile){
        console.log("profile input not found")
    }

    if(profile == "estudiante"){
    }

    if(profile == "mentor"){
        if(!localStorage.getItem("mentor_cleaned_data")){
            console.log("mentor_cleaned_data is not set on localStorage")
        }
    }
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

    init(){
        console.log(this.interests)
        console.log(this.formsetPrefix)
        console.log(this.mentor_exp.length)
        if(this.specialization_storage !== "No tengo especialización"){
            this.specialization = this.specialization_storage
        }
        // Do some checks
    },
    // submit_form(){
    //     // Get the form data
    //     const form = document.getElementById("form") as HTMLFormElement;
    //
    //     if(!form){
    //         console.log("could not get form")
    //         return
    //     }
    //
    //     if(!form.checkValidity()){
    //         console.log("form is not valid")
    //         return
    //     }
    //
    //     const formData = new FormData(form);
    //
    //     if(this.profile == "mentor"){
    //         const prefix = formData.get("formset-prefix")
    //
    //         if (!prefix) {console.warn("no prefix found fr"); return}
    //
    //         for (const expertise of this.mentor_exp){
    //             let i = 0
    //             for (const [key, value] of Object.entries(expertise)) {
    //                 formData.append(`${prefix}-${i}-${key}`, value)
    //                 i+=1
    //             }
    //         }
    //     }
    //
    //     debugger
    //     htmx.ajax("POST","", {
    //         values: Object.fromEntries(formData),
    //         target: "#form",
    //         swap: "outerHTML",
    //     }).then(()=>{
    //         console.log("form validated")
    //     })
    // },
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
