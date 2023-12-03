import Alpine from "alpinejs"

import { myAlpineComponent, startAlpine } from "js/utils/alpine"
import { profileStore } from "js/alpine_stores"

import {registerUrls} from "js/config/urls";

// Component definition
const select_spec = (urlCarrer: string) => ({
    specializations: [],
    search_key: "",

    // The selected from localstorage
    profile: Alpine.$persist("").as("profile"),

    // The selected carrer from localstorage
    carreer: Alpine.$persist('').as('carreer'),

    // The selected specialization from localstorage
    specialization_selected: Alpine.$persist("").as("specialization"),

    // The selected themes
    themes: Alpine.$persist<string[]>([]).as("themes"),

    // The carrer from the url path
    urlCarreer: urlCarrer,

    no_tengo: "No tengo especialización",

    // Some errors that might occur
    errorCarreer: false,
    errorProfile: false,

    /** builds a query parameter from the selected themes in the next step */
    buildThemeQuery(themes: string[]){
        const searchParams = new URLSearchParams("")

        // Only adds the query parameter if previous themes were selected
        themes.forEach((theme) => {
            searchParams.append("theme", theme)
        })

        searchParams.append("profile", this.profile)
        return `?${searchParams.toString()}`
    },

    init(){
        // Grab specializations names that came from the server
        this.specializations = JSON.parse(document.getElementById('specializations').textContent);

        // Add an special specializations for people that don't have one
        this.specializations.push(
            {name:this.no_tengo}
        )
        this.errorCarreer = this.carreer != urlCarrer
        this.errorProfile = this.profile == "mentor"

        this.$watch("specialization_selected", (newValue, oldValue)=>{
            // Reset the themes array since we now have a specialization selected
            console.log(`oldValue: ${oldValue}`);
            console.log(`newValue: ${newValue}`);
            if(oldValue === this.no_tengo){
                this.themes = []
            }
        })
    },

    /** crafts the url for the next step: choose themes */
    get next_url(){

        // If the user doesn't have a specialization, redirect to the interest themes page
        if (this.specialization_selected === this.no_tengo){

            const themes_url = registerUrls.select_themes(this.urlCarreer)

            // Add the selected themes as query parameters only if we have some
            if (this.themes.length > 0){
                return `${themes_url}${this.buildThemeQuery(this.themes)}`
            }

            return themes_url
        }

        // User does have a specialization, go to the final step
        return registerUrls.complete_profile(this.carreer, this.profile)
    },

    /** getter for filtering specializations names */
    get filteredSpecialization() {
        let filtSpecializationGroup = []
        filtSpecializationGroup = this.specializations.filter(
            specialization => {
                if (this.search_key != ""){
                    // Perform case insensitive search
                    const regex = new RegExp(this.search_key, "i")
                    return specialization.name.match(regex)
                }
                return specialization
            }
        )
        return filtSpecializationGroup
    },

})

const selectSpec: myAlpineComponent = {
    name: "select_spec",
    component: select_spec,
}

// Register component
startAlpine({
    components: [
        selectSpec
    ],
    stores: [
        profileStore
    ]
})
