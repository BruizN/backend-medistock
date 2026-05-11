workspace "Medistock" "Plataforma de comercio electrónico unificada para insumos médicos." {

    model {
        institucion = person "Institución (Clínica)" "Compra insumos médicos al por mayor."
        paciente = person "Paciente" "Compra insumos médicos (B2C)."
        
        medistockSystem = softwareSystem "Medistock E-Commerce" "Plataforma centralizada para venta y distribución de insumos." {
            
            singlePageApp = container "Frontend SPA (React)" "Proporciona toda la funcionalidad de compras al usuario" "Vite/React"
            
            apiApp = container "API RESTful (FastAPI)" "Provee servicios de catálogo, inventario, usuarios y órdenes" "Python/FastAPI" {
                authComponent = component "Auth Module" "Gestiona JWT y autenticación" "Python/FastAPI Router"
                inventoryComponent = component "Inventory Module" "Gestiona productos y stock" "Python/FastAPI Router"
                ordersComponent = component "Orders Module" "Gestiona pagos y órdenes" "Python/FastAPI Router"
                
                authComponent -> inventoryComponent "Verifica permisos"
                ordersComponent -> inventoryComponent "Verifica y descuenta stock"
            }
            database = container "Base de Datos" "Almacena información de productos, inventario, usuarios y órdenes" "PostgreSQL"
            storageVolume = container "Volumen de Datos" "Persistencia física de la base de datos" "Docker Volume (pg_data)"
            
            singlePageApp -> apiApp "Realiza llamadas API" "JSON/HTTPS"
            
            apiApp -> database "Lee de y escribe en" "SQL/AsyncPG"
            database -> storageVolume "Almacena datos en" "I/O"
        }

        erpSystem = softwareSystem "Sistemas ERP (Clínicas)" "Sistema externo que consume la API para abastecimiento automatizado."
        paymentGateway = softwareSystem "Pasarela de Pagos" "Procesa pagos (Webpay/MercadoPago)."
        currencyAPI = softwareSystem "API de Divisas" "Convierte moneda en tiempo real."
        
        institucion -> singlePageApp "Realiza pedidos institucionales"
        paciente -> singlePageApp "Realiza compras particulares"
        
        erpSystem -> apiApp "Consume catálogo y stock" "REST/HTTPS"
        
        ordersComponent -> paymentGateway "Inicia y valida pagos" "REST/HTTPS"
        ordersComponent -> currencyAPI "Solicita conversión" "REST/HTTPS"
    }

    views {
        systemContext medistockSystem "LogicalView" "Vista Lógica (System Context)" {
            include *
            autoLayout
        }

        container medistockSystem "DevelopmentView" "Vista de Desarrollo (Containers)" {
            include *
            autoLayout
        }

        component apiApp "ProcessView" "Vista de Procesos (Components)" {
            include *
            autoLayout
        }

        dynamic medistockSystem "ScenariosView" "Vista de Escenarios (Dynamic)" {
            paciente -> singlePageApp "1. Añade al carrito y checkout"
            singlePageApp -> apiApp "2. POST /orders"
            apiApp -> currencyAPI "3. Obtiene tipo de cambio"
            apiApp -> paymentGateway "4. Inicia transacción Webpay"
            apiApp -> database "5. Guarda orden pendiente"
            apiApp -> singlePageApp "6. Retorna URL de pago"
            autoLayout
        }
        
        deployment medistockSystem "Production" "PhysicalView" "Vista Física (Deployment)" {
            deploymentNode "AWS Cloud" {
                deploymentNode "EC2 Instance - Frontend" {
                    containerInstance singlePageApp
                }
                deploymentNode "EC2 Instance - Backend" {
                    containerInstance apiApp
                    containerInstance database
                    containerInstance storageVolume
                }
            }
        }

        theme default
    }
}
