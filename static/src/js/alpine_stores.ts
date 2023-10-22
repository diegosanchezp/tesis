import Alpine from "alpinejs"
import { myAlpineStore } from "js/utils/alpine"

/** Global store for instance comunication */
const profileStoreObj = ({profile}) =>({
    profile: profile,
    url: "",
    change(prfl: string){
        this.profile = prfl
    },
    set_url(url: string){
        this.url = url
    }
})

export const profileStore: myAlpineStore = {
    name: "profile",
    store: profileStoreObj,
    persist: true,
    persist_value: "profile", // property name
    as: "profile",
}
