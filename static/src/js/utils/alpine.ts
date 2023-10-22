import Alpine from "alpinejs"

export type myAlpineComponent = {
    name: string, component: () => any
}

export type myAlpineStore = {
    name: string, store: Object
}

export type startAlpineParams = {
    components: myAlpineComponent[]
    stores: myAlpineStore[]
}

export function startAlpine(params: startAlpineParams){
    // Init stores
    for (const store of params.stores){
        Alpine.store(store.name, store.store)
    }

    // Init components
    for (const component of params.components){
        Alpine.data(component.name, component.component)
    }

    Alpine.start()
}
