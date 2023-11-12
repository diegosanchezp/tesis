import Alpine from "alpinejs"
import { myAlpineComponent, startAlpine } from "js/utils/alpine"

// Component definition
const select_theme = (urlCarrer: string) => ({

    // The selected from localstorage
    profile: Alpine.$persist("").as("profile"),

    // The selected carrer from localstorage
    carreer: Alpine.$persist('').as('carreer'),

    // The selected specialization from localstorage
    specialization_selected: Alpine.$persist("").as("specialization"),

    // The carrer from the url path
    urlCarreer: urlCarrer,

    // The selected themes that come from the url
    urlThemes: [],

    // The selected themes
    themes: Alpine.$persist<string[]>([]).as("themes"),

    init(){
        this.urlThemes = JSON.parse(document.getElementById('url_themes').textContent)
    },

    get themes_query_url(){

        // Only make the url
        if (this.urlThemes.length == 0){
            return ""
        }

        const searchParams = new URLSearchParams()
        this.themes.forEach(
            (item)=>{
                searchParams.append("theme", item)
            }
        )
        return searchParams.toString()
    },

    get next_url(){
        return "Todo"
    },
})

const selectTheme: myAlpineComponent = {
    name: "select_theme",
    component: select_theme,
}

// Register component
startAlpine({
    components: [
        selectTheme
    ],
    stores: [
    ]
})
