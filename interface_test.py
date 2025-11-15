import re
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect, Page
import pytest
import time

@pytest.fixture(scope="session")
def browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    yield browser
    
    browser.close()
    playwright.stop()

@pytest.fixture(scope="session")
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:5173/financial")
    yield page
    context.close()

#Objetivo do teste: Validar o funcionamento do filtro de data e do botão filtrar
@pytest.mark.data_filtrar
def test_ct001_filtro_data_filtrar(page):
    #Clica no Botão Calendário
    page.click("#date-filter-btn")
    #Seleciona Mensal
    page.select_option(".select-control", "monthly")
    #Seleciona Anual
    page.select_option(".select-control", "year")
    #Seleciona Período
    page.select_option(".select-control", "period")
    #Seleciona Competência
    page.click("//*[@value='competencia']")
    #Clica em Filtrar
    page.click(".save-button")
    #Verifica se o filtro foi aplicado corretamente
    expect(page.locator(".title-label")).not_to_be_visible()
    print("✅ Filtro de data aplicado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão cancelar no filtro de data
@pytest.mark.data_cancelar
def test_ct002_filtro_data_cancelar(page):
    #Clica no Botão Calendário
    page.click("#date-filter-btn")
    #Clica em Cancel
    page.click(".cancel-button")
    #Verifica se o botão cancelar foi clicado
    expect(page.locator(".title-label")).not_to_be_visible()
    print("✅ Botão cancelar clicado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão limpar no filtro de data
@pytest.mark.data_limpar
def test_ct003_filtro_data_limpar(page):
    #Clica no Botão Calendário
    page.click("#date-filter-btn")
    #Clica em limpar
    page.click(".clear-button")
    #Verifica se o botão limpar foi clicado
    expect(page.locator('input[placeholder="Start date"]')).to_be_visible()
    print("✅ Botão limpar clicado corretamente.")


#Objetivo do teste: Validar o funcionamento do menu hamburguinho e a visibilidade do texto "Configure Card Preset"
@pytest.mark.hamburguinho_receitas_despesas
def test_ct004_hamburguinho_receitas_despesas(page):
    # Espera o botão estar visível e clica
    button = page.locator("#main-cards-menu-btn")
    button.wait_for(state="visible", timeout=10000)  # espera até 10s
    button.click()
    # Verifica se o texto "Configure Card Preset" está visível
    expect(page.get_by_text("Configure Card Preset")).to_be_visible()
    print("✅ Texto 'Configure Card Preset' está visível na tela.")


#Objetivo do teste: Validar o funcionamento dos check e uncheck dos switches do hamburguinho
@pytest.mark.hamburguinho_receitas_despesas_check
def test_ct005_receitas_hamburguinho_check_uncheck(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-preset-income-totalReceived-switch",
        "sample-preset-income-totalToReceive-switch",
        "sample-preset-income-totalCommittedIncome-switch",
        "sample-preset-expense-totalPaid-switch",
        "sample-preset-expense-totalToPay-switch",
        "sample-preset-expense-totalExpenses-switch",
    ]
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    for switch_id in switches:
        switch = page.locator(f"#{switch_id}")
        switch.wait_for(state="visible", timeout=5000)

        # Estado inicial (true ou false)
        estado_inicial = switch.get_attribute("aria-checked")
        print(f"🔎 {switch_id} antes do clique: {estado_inicial}")

        # Clica e valida mudança
        switch.click()
        if estado_inicial == "true":
            expect(switch).to_have_attribute("aria-checked", "false")
            print(f"✅ {switch_id} foi desmarcado")
        else:
            expect(switch).to_have_attribute("aria-checked", "true")
            print(f"✅ {switch_id} foi marcado")

        # (opcional) volta ao estado original
        switch.click()
        expect(switch).to_have_attribute("aria-checked", estado_inicial)


#Objetivo do teste: Validar o funcionamento do aviso ao desabilitar o último switch (Committed Despesas)
@pytest.mark.hamburguinho_receitas_aviso_ok
def test_ct006_receitas_hamburguinho_aviso_ok(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-preset-income-totalReceived-switch",
        "sample-preset-income-totalToReceive-switch",
        "sample-preset-income-totalCommittedIncome-switch",
        "sample-preset-expense-totalPaid-switch",
        "sample-preset-expense-totalToPay-switch",
        "sample-preset-expense-totalExpenses-switch",
    ]
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    for switch_id in switches:
        switch = page.locator(f"#{switch_id}")
        switch.wait_for(state="visible", timeout=5000)
        estado_inicial = switch.get_attribute("aria-checked")
        print(f"🔎 {switch_id} antes do clique: {estado_inicial}")
        if estado_inicial == "true":
            # Só clica se estiver marcado
            switch.click()
            print(f"✅ {switch_id} foi desmarcado porque estava marcado")
        else:
            # Se já estava desmarcado, só confirma
            print(f"⚪ {switch_id} já estava desmarcado, não clicou")

    # Verifica se o aviso está visível
    aviso = page.locator("text=Caso desabilite este card, todos os cards serão ocultados.")
    expect(aviso).to_be_visible()
    # Clica no botão OK do aviso
    page.locator("button:has-text('OK')").click()
    expect(aviso).not_to_be_visible()
    ultimo_check = page.locator("#sample-preset-expense-totalExpenses-switch")
    # Verifica se o último switch está desabilitado e desmarcado
    expect(ultimo_check).to_have_attribute("aria-checked", "true")
    expect(ultimo_check).to_be_disabled()
    print("✅ Aviso exibido e confirmado corretamente.")
    

#Objetivo do teste: Validar o funcionamento do botão cancelar no aviso ao desabilitar o último switch (Committed Despesas)
@pytest.mark.hamburguinho_receitas_aviso_cancelar
def test_ct007_receitas_hamburguinho_aviso_cancelar(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-preset-income-totalReceived-switch",
        "sample-preset-income-totalToReceive-switch",
        "sample-preset-income-totalCommittedIncome-switch",
        "sample-preset-expense-totalPaid-switch",
        "sample-preset-expense-totalToPay-switch",
        "sample-preset-expense-totalExpenses-switch",
    ]
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    for switch_id in switches:
        switch = page.locator(f"#{switch_id}")
        switch.wait_for(state="visible", timeout=5000)
        estado_inicial = switch.get_attribute("aria-checked")
        print(f"🔎 {switch_id} antes do clique: {estado_inicial}")
        if estado_inicial == "true":
            # Só clica se estiver marcado
            switch.click()
            print(f"✅ {switch_id} foi desmarcado porque estava marcado")
        else:
            # Se já estava desmarcado, só confirma
            print(f"⚪ {switch_id} já estava desmarcado, não clicou")
    # Verifica se o aviso está visível
    aviso = page.locator("text=Caso desabilite este card, todos os cards serão ocultados.")
    expect(aviso).to_be_visible()
    ultimo_check = page.locator("#sample-preset-expense-totalExpenses-switch")
    #Clica no botão cancelar
    page.locator("button:has-text('Cancel')").click()
    # Verifica se o último switch está habilitado e marcado novamente
    expect(ultimo_check).to_be_enabled()
    expect(ultimo_check).to_have_attribute("aria-checked", "true")
    print("✅ Aviso exibido e cancelado corretamente.") 


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Sessão Visisel"
@pytest.mark.hamburguinho_receitas_session_visible_switch
def test_ct008_receitas_hamburguinho_sessao_visivel(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza todos os switches na página
    session_visible_switch = page.locator("#preset-cards-sessao-visivel-switch")
    session_visible_switch.click()  # Clica para desmarcar
    print("✅ Sessão Visisel desmarcada.")
    #Verifica o sessão visisel está desmarcada
    expect(session_visible_switch).to_have_attribute("aria-checked", "false")
    session_visible_switch.click() # Clica para marcar novamente
    print("✅ Sessão Visisel marcada novamente.")
    #Verifica o sessão visisel está marcada
    expect(session_visible_switch).to_have_attribute("aria-checked", "true")
    

#Objetivo do teste: Validar o funcionamento do botão Habilitar Todos em Receitas
@pytest.mark.hamburguinho_receitas_habilitar_todos
def test_ct009_receitas_hamburguinho_habilitar_todos(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-preset-income-totalReceived-switch",
        "sample-preset-income-totalToReceive-switch",
        "sample-preset-income-totalCommittedIncome-switch",
        "sample-preset-expense-totalPaid-switch",
        "sample-preset-expense-totalToPay-switch",
        "sample-preset-expense-totalExpenses-switch",
    ]
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza todos os switches na página
    session_visible_switch = page.locator("#preset-cards-sessao-visivel-switch")
    session_visible_switch.click()  # Clica para desmarcar
    print("✅ Sessão Visisel desmarcada.")
   # Verifica se todos os switches estão inicialmente desabilitados
    for switch_id in switches:
        sw = page.locator(f"#{switch_id}")
        sw.wait_for(state="visible", timeout=5000)
        expect(sw).to_be_disabled(), f"Switch {switch_id} deveria estar desabilitado"
        print(f"✅ Switch {switch_id} está desabilitado conforme esperado.")
   # Clica no botão Habilitar Todos
    page.click("#drawer-enable-all-btn")
    print("✅ Botão 'Habilitar Todos' clicado.")
    # Verifica se todos os switches estão habilitados e marcados
    for switch_id in switches:
        sw = page.locator(f"#{switch_id}")
        sw.wait_for(state="visible", timeout=5000)
        expect(sw).to_be_enabled(), f"Switch {switch_id} deveria estar habilitado"
        expect(sw).to_have_attribute("aria-checked", "true"), f"Switch {switch_id} deveria estar marcado"
        print(f"✅ Switch {switch_id} está habilitado e marcado conforme esperado.")
            

#Objetivo do teste: Validar o funcionamento do botão fechar (X) no menu hamburguinho
@pytest.mark.hamburguinho_receitas_fechar
def test_ct010_receitas_hamburguinho_fechar(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Configure Card Preset")).not_to_be_visible()
    print("✅ Menu fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão salvar no menu hamburguinho
@pytest.mark.hamburguinho_receitas_salvar
def test_ct011_receitas_hamburguinho_salvar(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Verifica se o menu foi fechado
    aviso = page.locator("text=Card preset saved successfully!")
    expect(page.get_by_text("Configure Card Preset")).not_to_be_visible()
    expect(aviso).to_be_visible()
    print("✅ Menu salvo e fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Recebido"
@pytest.mark.hamburguinho_receitas_ocultar_recebido
def test_ct012_receitas_hamburguinho_ocultar_recebido(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_received = page.locator("#sample-preset-income-totalReceived-switch")
    # Verifica se está marcado
    if switch_received.get_attribute("aria-checked") == "true":
        switch_received.click()
        print("✅ Switch 'Recebido' desmarcado.")
    else:
        print("ℹ️ Switch 'Recebido' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Usando o seletor de classe + texto
    recebido = page.locator("h3.card-title:text('Total Received')")
    expect(recebido).not_to_be_visible()
    print("✅ Switch 'Recebido' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Receber"
@pytest.mark.hamburguinho_receitas_ocultar_receber
def test_ct013_receitas_hamburguinho_ocultar_receber(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_to_receive = page.locator("#sample-preset-income-totalToReceive-switch")
    # Verifica se está marcado
    if switch_to_receive.get_attribute("aria-checked") == "true":
        switch_to_receive.click()
        print("✅ Switch 'Receber' desmarcado.")
    else:
        print("ℹ️ Switch 'Receber' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Usando o seletor de classe + texto
    receber = page.locator("h3.card-title:text('Total To Receive')")
    expect(receber).not_to_be_visible()
    print("✅ Switch 'Receber' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Committed Receitas"
@pytest.mark.hamburguinho_receitas_ocultar_comprometido_receitas
def test_ct014_receitas_hamburguinho_ocultar_comprometido_receitas(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_committed_income = page.locator("#sample-preset-income-totalCommittedIncome-switch")
    # Verifica se está marcado
    if switch_committed_income.get_attribute("aria-checked") == "true":
        switch_committed_income.click()
        print("✅ Switch 'Receitas comprometido' desmarcado.")
    else:
        print("ℹ️ Switch 'Receitas comprometido' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Usando o seletor de classe + texto
    comprometido_receitas_= page.locator("h3.card-title:text('Committed')").nth(1)
    expect(comprometido_receitas_).not_to_be_visible()
    print("✅ Switch 'Committed' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Pago"
@pytest.mark.hamburguinho_receitas_ocultar_pago
def test_ct015_receitas_hamburguinho_ocultar_pago(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_paid = page.locator("#sample-preset-expense-totalPaid-switch")
    # Verifica se está marcado
    if switch_paid.get_attribute("aria-checked") == "true":
        switch_paid.click()
        print("✅ Switch 'Pago' desmarcado.")
    else:
        print("ℹ️ Switch 'Pago' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Usando o seletor de classe + texto
    pago = page.locator("h3.card-title:text('Total Paid')")
    expect(pago).not_to_be_visible()
    print("✅ Switch 'Pago' ocultado corretamente.")
    

#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Pagar"
@pytest.mark.hamburguinho_receitas_ocultar_pagar
def test_ct016_receitas_hamburguinho_ocultar_pagar(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_to_pay = page.locator("#sample-preset-expense-totalToPay-switch")
    # Verifica se está marcado
    if switch_to_pay.get_attribute("aria-checked") == "true":
        switch_to_pay.click()
        print("✅ Switch 'Pagar' desmarcado.")
    else:
        print("ℹ️ Switch 'Pagar' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Usando o seletor de classe + texto
    pagar = page.locator("h3.card-title:text('Total To Pay')")
    expect(pagar).not_to_be_visible()
    print("✅ Switch 'Pagar' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Committed Despesas"
@pytest.mark.hamburguinho_receitas_ocultar_comprometido_despesas
def test_ct017_receitas_hamburguinho_ocultar_comprometido_despesas(page):
    # Pega o botão menu apenas do primeiro card (despesas)
    page.locator("#main-cards-menu-btn").click()
    # Localiza o switch
    switch_expenses_committed = page.locator("#sample-preset-expense-totalExpenses-switch")
    # Verifica se está marcado
    if switch_expenses_committed.get_attribute("aria-checked") == "true":
        switch_expenses_committed.click()
        print("✅ Switch 'Despesas Committed' desmarcado.")
    else:
        print("ℹ️ Switch 'Despesas Committed' já estava desmarcado.")
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Localiza o card pelo título "Committed" dentro do h3
    card_comprometido = page.locator("div.card:has(h3.card-title:text('Committed'))").nth(1)
    # Verifica que **não está visível**
    expect(card_comprometido).not_to_be_visible()
    print("✅ Switch 'Committed' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão Exit without saving no menu hamburguinho
@pytest.mark.hamburguinho_receitas_sair_sem_salvar
def test_ct018_receitas_hamburguinho_sair_sem_salvar(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Desmarca o switch "Pagar" (5º switch, índice 5)
    switches = page.locator("button[role='switch']")
    switches.nth(5).click()  # Clica para desmarcar
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    aviso = page.locator("text=There are unsaved changes")
    expect(aviso).to_be_visible()
    # Clica no botão Exit without saving
    page.locator("button:has-text('Exit without saving')").click()
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Configure Card Preset")).not_to_be_visible()
    print("✅ Menu fechado sem salvar corretamente.")


#Objetivo do teste: Validar o funcionamento do botão Exit without saving no menu hamburguinho
@pytest.mark.hamburguinho_receitas_retornar_configuracoes
def test_ct019_receitas_hamburguinho_retornar_configuracoes(page):
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#main-cards-menu-btn").click()
    # Desmarca o switch "Pagar" (5º switch, índice 5)
    switches = page.locator("button[role='switch']")
    switches.nth(5).click()  # Clica para desmarcar
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    aviso = page.locator("text=There are unsaved changes")
    expect(aviso).to_be_visible()
    # Clica no botão Revert changes
    page.locator("button:has-text('Revert changes')").click()
    # Verifica se o menu ainda está aberto
    expect(page.get_by_text("Configure Card Preset")).to_be_visible()
    print("✅ Menu permaneceu aberto após retornar as configurações.")


#Objetivo do teste: Validar o funcionamento do menu hamburguinho e a visibilidade do texto "Sample Flow Presets"
@pytest.mark.hamburguinho_fluxo_caixa
def test_ct020_hamburguinho_fluxo_caixa(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    menu_button = page.locator("#sample-flow-menu-btn")
    menu_button.click()
    # Verifica se o texto "Sample Flow Presets" está visível
    expect(page.get_by_text("Sample Flow Presets")).to_be_visible()
    print("✅ Texto 'Sample Flow Presets' está visível na tela.")
    

#Objetivo do teste: Validar o funcionamento do check e uncheck dos switches do hamburguinho do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_check_uncheck
def test_ct021_hamburguinho_fluxo_caixa_check_uncheck(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-flow-opcao-grouped-switch",
        "sample-flow-opcao-stacked-switch",
        "sample-flow-opcao-list-switch",
        "sample-flow-freq-diario-switch",
        "sample-flow-freq-semanal-switch",
        "sample-flow-freq-mensal-switch",
        "sample-flow-freq-trimestral-switch",
        "sample-flow-freq-semestral-switch",
        "sample-flow-freq-anual-switch",
        "sample-flow-freq-todos-switch"
    ]
    # Pega o botão menu apenas do primeiro card (Receitas)
    page.locator("#sample-flow-menu-btn").click()
    for switch_id in switches:
        switch = page.locator(f"#{switch_id}")
        switch.wait_for(state="visible", timeout=5000)

        # Estado inicial (true ou false)
        estado_inicial = switch.get_attribute("aria-checked")
        print(f"🔎 {switch_id} antes do clique: {estado_inicial}")

        # Clica e valida mudança
        switch.click()
        if estado_inicial == "true":
            expect(switch).to_have_attribute("aria-checked", "false")
            print(f"✅ {switch_id} foi desmarcado")
        else:
            expect(switch).to_have_attribute("aria-checked", "true")
            print(f"✅ {switch_id} foi marcado")

        # (opcional) volta ao estado original
        switch.click()
        expect(switch).to_have_attribute("aria-checked", estado_inicial)


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Sessão Visisel" do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_session_visible_switch
def test_ct022_fluxo_caixa_hamburguinho_sessao_visivel(page):
    # Abre o menu do primeiro card (Receitas)
    page.locator("#sample-flow-menu-btn").click()
    # Clica no switch "Sessão Visível" para desmarcar
    session_visible_switch = page.locator("#sample-flow-sessao-visivel-switch")
    session_visible_switch.click()
    print("✅ Sessão Visisel desmarcada.")
    # Verifica que realmente está desmarcada
    expect(session_visible_switch).to_have_attribute("aria-checked", "false")
    # Marca novamente
    session_visible_switch.click()
    print("✅ Sessão Visisel marcada novamente.")
    # Verifica que realmente está marcada
    expect(session_visible_switch).to_have_attribute("aria-checked", "true")


#Objetivo do teste: Validar o funcionamento do botão Habilitar Todos do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_habilitar_todos
def test_ct023_fluxo_caixa_hamburguinho_habilitar_todos(page):
    # Lista dos IDs dos switches
    switches = [
        "sample-flow-opcao-grouped-switch",
        "sample-flow-opcao-stacked-switch",
        "sample-flow-opcao-list-switch",
        "sample-flow-freq-diario-switch",
        "sample-flow-freq-semanal-switch",
        "sample-flow-freq-mensal-switch",
        "sample-flow-freq-trimestral-switch",
        "sample-flow-freq-semestral-switch",
        "sample-flow-freq-anual-switch",
        "sample-flow-freq-todos-switch"
    ]
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em sessão visível
    page.locator("#sample-flow-sessao-visivel-switch").click()
    print("✅ Sessão Visisel desmarcada.")
    # Clica no botão "Habilitar Todos"
    page.locator("#drawer-enable-all-btn").click()
    print("✅ Botão 'Habilitar Todos' clicado.")
    for switch_id in switches:
        switch = page.locator(f"#{switch_id}")
        switch.wait_for(state="visible", timeout=5000)
        # Verifica que o switch está habilitado
        expect(switch).to_be_enabled()
        print(f"✅ {switch_id} está habilitado conforme esperado.")


#Objetivo do teste: Validar o funcionamento do botão fechar (X) no menu hamburguinho do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_fechar
def test_ct024_fluxo_caixa_hamburguinho_fechar(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Sample Flow Presets")).not_to_be_visible()
    print("✅ Menu fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão salvar no menu hamburguinho do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_salvar
def test_ct025_fluxo_caixa_hamburguinho_salvar(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Verifica se o menu foi fechado
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(page.get_by_text("Sample Flow Presets")).not_to_be_visible()
    expect(aviso).to_be_visible()
    print("✅ Menu salvo e fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão Exit without saving no menu hamburguinho do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_sair_sem_salvar
def test_ct026_fluxo_caixa_hamburguinho_sair_sem_salvar(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    page.locator("#sample-flow-freq-semestral-switch").click()  # Clica para desmarcar
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    aviso = page.locator("text=There are unsaved changes")
    expect(aviso).to_be_visible()
    # Clica no botão Exit without saving
    page.locator("button:has-text('Exit without saving')").click()
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Sample Flow Presets")).not_to_be_visible()
    print("✅ Menu fechado sem salvar corretamente.")


#Objetivo do teste: Validar o funcionamento do botão Revert changes no menu hamburguinho do card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_retornar_configuracoes
def test_ct027_fluxo_caixa_hamburguinho_retornar_configuracoes(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    page.locator("#sample-flow-freq-semestral-switch").click()  # Clica para desmarcar
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    aviso = page.locator("text=There are unsaved changes")
    expect(aviso).to_be_visible()
    # Clica no botão Revert changes
    page.locator("button:has-text('Revert changes')").click()
    # Verifica se o menu ainda está aberto
    expect(page.get_by_text("Sample Flow Presets")).to_be_visible()
    print("✅ Menu permaneceu aberto após retornar as configurações.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_lista
def test_ct028_fluxo_caixa_hamburguinho_visualizacao_lista(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Lista
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em lista foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Verifica se a tabela está visível
    descricao = page.locator("span.ag-header-cell-text", has_text="Descrição")
    expect(descricao).to_be_visible()
    print("✅ Visualização em lista aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado
def test_ct029_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Verifica se o gráfico está visível
    diario_span = page.locator("span", has_text="Diário").nth(0)
    expect(diario_span).to_be_visible()
    print("✅ Visualização em gráfico agrupado aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao
def test_ct030_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico por Visão
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico por visão foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Verifica se o gráfico está visível
    entrada_btn = page.locator("button", has_text="Entrada - Entrada Aporte Capital, Legend item 1 of 12")
    expect(entrada_btn).to_be_visible()
    print("✅ Visualização em gráfico por visão aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência diário no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_diario
def test_ct031_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_diario(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Diário
    page.locator("div.ant-select-item-option-content:text('Diário')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    diario_button = page.locator("button:has(span:text('Diário'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(diario_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência diário aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência semanal no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_semanal
def test_ct032_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_semanal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Semanal
    page.locator("div.ant-select-item-option-content:text('Semanal')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    semanal_button = page.locator("button:has(span:text('Semanal'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(semanal_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência semanal aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência mensal no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_mensal
def test_ct033_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_mensal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Mensal
    page.locator("div.ant-select-item-option-content:text('Mensal')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    mensal_button = page.locator("button:has(span:text('Mensal'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(mensal_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência mensal aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência trimestral no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_trimestral
def test_ct034_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_trimestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Trimestral
    page.locator("div.ant-select-item-option-content:text('Trimestral')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    trimestral_button = page.locator("button:has(span:text('Trimestral'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(trimestral_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência trimestral aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência semanal no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_semestral
def test_ct035_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_semestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Semestral
    page.locator("div.ant-select-item-option-content:text('Semestral')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    semestral_button = page.locator("button:has(span:text('Semestral'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(semestral_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência semestral aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência anual no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_anual
def test_ct036_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_anual(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Anual
    page.locator("div.ant-select-item-option-content:text('Anual')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_agrupado = page.locator("button:has(div:text('Gráfico agrupado'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_agrupado).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    anual_button = page.locator("button:has(span:text('Anual'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(anual_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico agrupado com frequência anual aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico agrupado com frequência agrupado no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_agrupado_frequencia_agrupado
def test_ct037_fluxo_caixa_hamburguinho_visualizacao_grafico_agrupado_frequencia_agrupado(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico Agrupado')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Todos
    page.locator("div.ant-select-item-option-content:text('Todos')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    agrupado_button = page.locator("button:has(span:text('Agrupado'))").nth(0)
    # Verifica se o botão está visível
    expect(agrupado_button).to_be_visible()
    print("✅ Visualização em gráfico agrupado com frequência agrupado aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência diário no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_diario
def test_ct039_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_diario(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Diário
    page.locator("div.ant-select-item-option-content:text('Diário')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    diario_button = page.locator("button:has(span:text('Diário'))").nth(0)
    # Verifica se o botão está visível
    expect(diario_button).to_be_visible()
    print("✅ Visualização em gráfico por visão com frequência diário aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência semanal no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_semanal
def test_ct038_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_semanal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Semanal
    page.locator("div.ant-select-item-option-content:text('Semanal')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    semanal_button = page.locator("button:has(span:text('Semanal'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(semanal_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência semanal aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência mensal no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_mensal
def test_ct040_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_mensal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Mensal
    page.locator("div.ant-select-item-option-content:text('Mensal')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    mensal_button = page.locator("button:has(span:text('Mensal'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(mensal_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência mensal aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência trimestral no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_trimestral
def test_ct041_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_trimestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Trimestral
    page.locator("div.ant-select-item-option-content:text('Trimestral')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    trimestral_button = page.locator("button:has(span:text('Trimestral'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(trimestral_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência trimestral aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência semestral no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_semestral
def test_ct042_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_semestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Semestral
    page.locator("div.ant-select-item-option-content:text('Semestral')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    semestral_button = page.locator("button:has(span:text('Semestral'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(semestral_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência semestral aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência anual no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_anual
def test_ct043_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_anual(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Anual
    page.locator("div.ant-select-item-option-content:text('Anual')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    # Verifica se o gráfico está visível
    anual_button = page.locator("button:has(span:text('Anual'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(anual_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência anual aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de visualização em gráfico por visão com frequência agrupado no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_visualizacao_grafico_por_visao_frequencia_agrupado
def test_ct044_fluxo_caixa_hamburguinho_visualizacao_grafico_por_visao_frequencia_agrupado(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Gráfico Agrupado
    page.locator("div.ant-select-item-option-content:text('Gráfico por Visão')").click()
    # Clica em opção de frequência 
    page.locator("div.ant-select").nth(1).click()
    # Seleciona a opção Todos
    page.locator("div.ant-select-item-option-content:text('Todos')").click()
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se a visualização em gráfico agrupado foi aplicada
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    # Localiza o botão pelo texto dentro do span/div
    grafico_por_visao = page.locator("button:has(div:text('Gráfico por Visão'))").nth(0)
    # Espera que ele tenha a classe active
    expect(grafico_por_visao).to_have_class(re.compile(".*active.*"))
    agrupado_button = page.locator("button:has(span:text('Agrupado'))").nth(0)
    # Verifica se o botão possui a classe active
    expect(agrupado_button).to_have_class(re.compile(".*active.*"))
    print("✅ Visualização em gráfico por visão com frequência agrupado aplicada corretamente.")


#Objetivo do teste: Validar o funcionamento da opção de colunas na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista
def test_ct045_fluxo_caixa_hamburguinho_colunas_lista(page):
    checkbox_ids = [
    "sample-flow-coluna-realizado-checkbox",
    "sample-flow-coluna-realizar-checkbox",
    "sample-flow-coluna-comprometido-checkbox",
    "sample-flow-coluna-projecao-checkbox",
    "sample-flow-coluna-projetado-checkbox"
    ]
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Clica em opção de visualização 
    page.locator("div.ant-select").nth(0).click()
    # Seleciona a opção Lista
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    for checkbox_id in checkbox_ids:
        checkbox_span = page.locator(f"#{checkbox_id}")
        # Verifica se está marcado pelo atributo class
        is_checked = "ant-checkbox-checked" in checkbox_span.get_attribute("class")
        if not is_checked:
            checkbox_span.click()  # marca
            page.wait_for_timeout(300)
            print(f"✅ Checkbox '{checkbox_id}' foi marcado.")
            checkbox_span.click()  # desmarca
            print(f"ℹ️ Checkbox '{checkbox_id}' marcado novamente.")
        else:
            print(f"ℹ️ Checkbox '{checkbox_id}' já estava marcado.")
            checkbox_span.click()  # desmarca
            print(f"✅ Checkbox '{checkbox_id}' desmarcado.")
            checkbox_span.click()  # marca de novo
            print(f"✅ Checkbox '{checkbox_id}' marcado novamente.")
        

#Objetivo do teste: Validar o funcionamento da opção de ocultar a coluna Realizado na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista_ocultar_realizado
def test_ct046_fluxo_caixa_hamburguinho_colunas_lista_ocultar_realizado(page):
    page.locator("#sample-flow-menu-btn").click()
    page.locator("div.ant-select").nth(0).click()
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    realizado_checkbox_input = page.locator("#sample-flow-coluna-realizado-checkbox")
    # Desmarca somente se estiver marcado
    if realizado_checkbox_input.is_checked():
        realizado_checkbox_input.click(force=True)
    expect(realizado_checkbox_input).not_to_be_checked()
    print("✅ Checkbox 'Realizado' está desmarcado.")
    page.click("button:has-text('Save')")
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após ocultar a coluna 'Realizado'.")
    col_realizado = page.locator("th:has-text('Realizado')")
    expect(col_realizado).not_to_be_visible()
    print("✅ Coluna 'Realizado' não está mais visível na tabela.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a coluna A Realizar na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista_ocultar_a_realizar
def test_ct047_fluxo_caixa_hamburguinho_colunas_lista_ocultar_a_realizar(page):
    page.locator("#sample-flow-menu-btn").click()
    page.locator("div.ant-select").nth(0).click()
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    realizar_checkbox_input = page.locator("#sample-flow-coluna-realizar-checkbox")
    # Desmarca somente se estiver marcado
    if realizar_checkbox_input.is_checked():
        realizar_checkbox_input.click(force=True)
    expect(realizar_checkbox_input).not_to_be_checked()
    print("✅ Checkbox 'A Realizar' está desmarcado.")
    page.click("button:has-text('Save')")
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após ocultar a coluna 'A Realizar'.")
    col_a_realizar = page.locator("th:has-text('A Realizar')")
    expect(col_a_realizar).not_to_be_visible()
    print("✅ Coluna 'A Realizar' não está mais visível na tabela.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a coluna Committed na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista_comprometido
def test_ct048_fluxo_caixa_hamburguinho_colunas_lista_ocultar_comprometido(page):
    page.locator("#sample-flow-menu-btn").click()
    page.locator("div.ant-select").nth(0).click()
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    comprometido_checkbox_input = page.locator("#sample-flow-coluna-comprometido-checkbox")
    # Desmarca somente se estiver marcado
    if comprometido_checkbox_input.is_checked():
        comprometido_checkbox_input.click(force=True)
    expect(comprometido_checkbox_input).not_to_be_checked()
    print("✅ Checkbox 'Committed' está desmarcado.")
    page.click("button:has-text('Save')")
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()

    print("✅ Preset salvo com sucesso após ocultar a coluna 'Committed'.")
    col_comprometido = page.locator("th:has-text('Committed')")
    expect(col_comprometido).not_to_be_visible()
    print("✅ Coluna 'Committed' não está mais visível na tabela.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a coluna Projeção na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista_ocultar_projecao
def test_ct049_fluxo_caixa_hamburguinho_colunas_lista_ocultar_projecao(page):
    page.locator("#sample-flow-menu-btn").click()
    page.locator("div.ant-select").nth(0).click()
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    projecao_checkbox_input = page.locator("#sample-flow-coluna-projecao-checkbox")
    # Desmarca somente se estiver marcado
    if projecao_checkbox_input.is_checked():
        projecao_checkbox_input.click(force=True)
    expect(projecao_checkbox_input).not_to_be_checked()
    print("✅ Checkbox 'Projeção' está desmarcado.")
    # Clica em salvar
    page.click("button:has-text('Save')")
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após ocultar a coluna 'Projeção'.")
    # Verifica se a coluna 'Projeção' realmente sumiu da tabela
    col_projecao = page.locator("th:has-text('Projeção')")
    expect(col_projecao).not_to_be_visible(timeout=5000)  # espera até 5s para a coluna sumir
    print("✅ Coluna 'Projeção' não está mais visível na tabela.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a coluna Projetado na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_colunas_lista_ocultar_projetado
def test_ct050_fluxo_caixa_hamburguinho_colunas_lista_ocultar_projetado(page):
    page.locator("#sample-flow-menu-btn").click()
    page.locator("div.ant-select").nth(0).click()
    page.locator("div.ant-select-item-option-content:text('Lista')").click()
    projetado_checkbox_input = page.locator("#sample-flow-coluna-projetado-checkbox")
    # Desmarca somente se estiver marcado
    if projetado_checkbox_input.is_checked():
        projetado_checkbox_input.click(force=True)
    expect(projetado_checkbox_input).not_to_be_checked()
    print("✅ Checkbox 'Projetado' está desmarcado.")
    # Clica em salvar
    page.click("button:has-text('Save')")
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após ocultar a coluna 'Projetado'.")
    # Verifica se a coluna 'Projetado' realmente sumiu da tabela
    col_projetado = page.locator("th:has-text('Projetado')")
    expect(col_projetado).not_to_be_visible(timeout=5000)  # espera até 5s para a coluna sumir
    print("✅ Coluna 'Projetado' não está mais visível na tabela.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar o gráfico agrupado no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_grafico_agrupado
def test_ct051_fluxo_caixa_hamburguinho_ocultar_checkbox_grafico_agrupado(page):
     # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    #Desmarca gráfico agrupado
    page.locator("#sample-flow-opcao-grouped-switch").click()
    checkbox_grafico_agrupado = page.locator("#sample-flow-opcao-grouped-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_grafico_agrupado.get_attribute("class"):
        checkbox_grafico_agrupado.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Gráfico Agrupado' foi desativado.")
    else:
        print("ℹ️ Switch 'Gráfico Agrupado' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Gráfico Agrupado'.")
    # Verifica se o gráfico agrupado não está mais visível
    grafico_agrupado = page.locator("//*[name()='svg' and @class='recharts-surface']")
    expect(grafico_agrupado).not_to_be_visible()
    print("✅ Gráfico Agrupado não está mais visível no card Fluxo de Caixa.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar o gráfico por visão no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_grafico_por_visao
def test_ct052_fluxo_caixa_hamburguinho_ocultar_checkbox_grafico_por_visao(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_grafico_por_visao = page.locator("#sample-flow-opcao-stacked-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_grafico_por_visao.get_attribute("class"):
        checkbox_grafico_por_visao.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Gráfico por Visão' foi desativado.")
    else:
        print("ℹ️ Switch 'Gráfico por Visão' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Gráfico por Visão'.")
    # Verifica se o gráfico por visão não está mais visível
    grafico_por_visao = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_por_visao).not_to_be_visible()
    print("✅ Gráfico por Visão não está mais visível no card Fluxo de Caixa.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a lista na visualização em lista no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_lista
def test_ct053_fluxo_caixa_hamburguinho_ocultar_checkbox_lista(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_lista = page.locator("#sample-flow-opcao-list-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_lista.get_attribute("class"):
        checkbox_lista.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Lista' foi desativado.")
    else:
        print("ℹ️ Switch 'Lista' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Lista'.")
    # Verifica se a lista (tabela) não está mais visível
    lista = page.locator("table")
    time.sleep(2)  # espera a tabela desaparecer
    expect(lista).not_to_be_visible()
    print("✅ Lista não está mais visível no card Fluxo de Caixa.")



#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'diário' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_diario
def test_ct054_fluxo_caixa_hamburguinho_ocultar_checkbox_diario(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_diario = page.locator("#sample-flow-freq-diario-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_diario.get_attribute("class"):
        checkbox_diario.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Diário' foi desativado.")
    else:
        print("ℹ️ Switch 'Diário' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Diário'.")
    # Verifica se o gráfico Diário não está mais visível
    grafico_diario = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_diario).not_to_be_visible()
    print("✅ Gráfico Diário não está mais visível no card Fluxo de Caixa.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'semanal' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_semanal
def test_ct055_fluxo_caixa_hamburguinho_ocultar_checkbox_semanal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_semanal = page.locator("#sample-flow-freq-semanal-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_semanal.get_attribute("class"):
        checkbox_semanal.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Semanal' foi desativado.")
    else:
        print("ℹ️ Switch 'Semanal' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Semanal'.")
    # Verifica se o gráfico Semanal não está mais visível
    grafico_semanal = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_semanal).not_to_be_visible()
    print("✅ Gráfico Semanal não está mais visível no card Fluxo de Caixa.")



#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'mensal' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_mensal
def test_ct056_fluxo_caixa_hamburguinho_ocultar_checkbox_mensal(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_mensal = page.locator("#sample-flow-freq-mensal-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_mensal.get_attribute("class"):
        checkbox_mensal.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Mensal' foi desativado.")
    else:
        print("ℹ️ Switch 'Mensal' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Mensal'.")
    # Verifica se o gráfico Mensal não está mais visível
    grafico_mensal = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_mensal).not_to_be_visible()
    print("✅ Gráfico Mensal não está mais visível no card Fluxo de Caixa.")



#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'trimestral' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_trimestral
def test_ct057_fluxo_caixa_hamburguinho_ocultar_checkbox_trimestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_trimestral = page.locator("#sample-flow-freq-trimestral-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_trimestral.get_attribute("class"):
        checkbox_trimestral.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Trimestral' foi desativado.")
    else:
        print("ℹ️ Switch 'Trimestral' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Trimestral'.")
    # Verifica se o gráfico trimestral não está mais visível
    grafico_trimestral = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_trimestral).not_to_be_visible()
    print("✅ Gráfico Trimestral não está mais visível no card Fluxo de Caixa.")



#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'semestral' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_semestral
def test_ct058_fluxo_caixa_hamburguinho_ocultar_checkbox_semestral(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_semestral = page.locator("#sample-flow-freq-semestral-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_semestral.get_attribute("class"):
        checkbox_semestral.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Semestral' foi desativado.")
    else:
        print("ℹ️ Switch 'Semestral' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Semestral'.")
    # Verifica se o gráfico semestral não está mais visível
    grafico_semestral = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_semestral).not_to_be_visible()
    print("✅ Gráfico Semestral não está mais visível no card Fluxo de Caixa.")



#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'anual' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_anual
def test_ct059_fluxo_caixa_hamburguinho_ocultar_checkbox_anual(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_anual = page.locator("#sample-flow-freq-anual-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_anual.get_attribute("class"):
        checkbox_anual.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Anual' foi desativado.")
    else:
        print("ℹ️ Switch 'Anual' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Anual'.")
    # Verifica se o gráfico anual não está mais visível
    grafico_anual = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_anual).not_to_be_visible()
    print("✅ Gráfico Anual não está mais visível no card Fluxo de Caixa.")


#Objetivo do teste: Validar o funcionamento da opção de ocultar a frequência 'agrupado' no card Fluxo de Caixa
@pytest.mark.hamburguinho_fluxo_caixa_ocultar_checkbox_agrupado
def test_ct060_fluxo_caixa_hamburguinho_ocultar_checkbox_agrupado(page):
    # Pega o botão menu apenas do card Fluxo de Caixa
    page.locator("#sample-flow-menu-btn").click()
    # Pega o switch pelo ID
    checkbox_agrupado = page.locator("#sample-flow-freq-todos-switch")
    # Verifica se o switch está marcado (classe "ant-switch-checked")
    if "ant-switch-checked" in checkbox_agrupado.get_attribute("class"):
        checkbox_agrupado.click()  # desmarca
        page.wait_for_timeout(300)  # pequeno delay opcional
        print("✅ Switch 'Agrupado' foi desativado.")
    else:
        print("ℹ️ Switch 'Agrupado' já estava desativado.")
    # Clica em Save
    page.click("button:has-text('Save')")
    # Verifica se o aviso de sucesso apareceu
    aviso = page.locator("text=Flow preset saved successfully!")
    expect(aviso).to_be_visible()
    print("✅ Preset salvo com sucesso após desativar o switch 'Agrupado'.")
    # Verifica se o gráfico agrupado não está mais visível
    grafico_agrupado = page.locator("//*[name()='svg' and @class='recharts-surface']")
    time.sleep(2)  # espera o gráfico desaparecer
    expect(grafico_agrupado).not_to_be_visible()
    print("✅ Gráfico Agrupado não está mais visível no card Fluxo de Caixa.")


#Objetivo do teste: Validar o funcionamento do botão "editar" do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_editar
def test_ct061_hamburguinho_padrao_editar(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()


#Objetivo do teste: Validar o funcionamento da opção "editar nome" do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_editar_nome
def test_ct062_hamburguinho_padrao_editar_nome(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar pelo texto do botão
    page.locator("button:has-text('Editar nome')").click()
    # Selecionar o input e preencher com "Padrão"
    page.locator("input.ant-input").fill("PADRÃO")
    # Clicar no botão pelo aria-label
    page.locator("button[aria-label='Save nome']").click()
    aviso = page.locator("text=Nome do preset atualizado com sucesso!")
    expect(aviso).to_be_visible()
    print("✅ Nome alterado com sucesso.")
    page.locator("button:has-text('Editar nome')").click()
    page.locator("input.ant-input").fill("Padrão")
    page.locator("button[aria-label='Save nome']").click()


#Objetivo do teste: Validar o funcionamento da opção "cancelar edição do nome"  do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_editar_nome_clicarX
def test_ct063_hamburguinho_padrao_editar_nome_clicarX(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar pelo texto do botão
    page.locator("button:has-text('Editar nome')").click()
     # Clica no botão "Cancel edição" usando o aria-label
    page.locator("button[aria-label='Cancel edição']").click()
    # Expect: verifica que o botão "Editar nome" está visível
    expect(page.locator("button:has-text('Editar nome')")).to_be_visible()
    print("✅ Edição do nome cancelada com sucesso.")


#Objetivo do teste: Validar o funcionamento da opção "sessão visível" dos cards receitas/despesas do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_sessao_visivel_cards
def test_ct064_hamburguinho_padrao_sessao_visivel_cards(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no collapse header pelo texto
    collpase = page.locator("div.ant-collapse-header:has-text('Cards Receitas/Despesas')")
    collpase.click()
    #Clica novamente para o sessão visível/invisível ficar visível
    collpase.click()
    switch_button = page.locator("button[role='switch'] >> span:has-text('Sessão visível')").nth(2)
    # Clica para alternar para 'Sessão Oculta'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão Oculta")
    # Clica novamente para voltar para 'Sessão visível'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão visível")


#Objetivo do teste: Validar o funcionamento da opção "sessão visível" dos Filtros Financeiros do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_sessao_visivel_filtros_financeiros
def test_ct065_hamburguinho_padrao_sessao_visivel_filtros_financeiros(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no collapse header pelo texto
    collpase = page.locator("div.ant-collapse-header:has-text('Filtros Financeiros')")
    collpase.click()
    #Clica novamente para o sessão visível/invisível ficar visível
    collpase.click()
    switch_button = page.locator("button[role='switch'] >> span:has-text('Sessão visível')").first
    # Clica para alternar para 'Sessão Oculta'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão Oculta")
    # Clica novamente para voltar para 'Sessão visível'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão visível")


#Objetivo do teste: Validar o funcionamento da opção "sessão visível" do fluxo de caixa do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_sessao_visivel_fluxo_caixa
def test_ct066_hamburguinho_padrao_sessao_visivel_fluxo_caixa(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no collapse header pelo texto Fluxo de Caixa
    collpase = page.locator("div.ant-collapse-header:has-text('Fluxo de Caixa')")
    collpase.click()
    #Clica novamente para o sessão visível/invisível ficar visível
    collpase.click()
    switch_button = page.locator("button[role='switch'] >> span:has-text('Sessão visível')").nth(4)
    # Clica para alternar para 'Sessão Oculta'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão Oculta")
    # Clica novamente para voltar para 'Sessão visível'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão visível")


#Objetivo do teste: Validar o funcionamento da opção "sessão visível" do Resumos Financeiros do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_sessao_visivel_resumos_financeiros
def test_ct067_hamburguinho_padrao_sessao_visivel_resumos_financeiros(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no collapse header pelo texto Resumos Financeiros
    collpase = page.locator("div.ant-collapse-header:has-text('Resumos Financeiros')")
    collpase.click()
    #Clica novamente para o sessão visível/invisível ficar visível
    collpase.click()
    switch_button = page.locator("button[role='switch'] >> span:has-text('Sessão visível')").nth(6)
    # Clica para alternar para 'Sessão Oculta'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão Oculta")
    # Clica novamente para voltar para 'Sessão visível'
    switch_button.click()
    expect(switch_button).to_contain_text("Sessão visível")


#Objetivo do teste: Validar o funcionamento da opção "salvar" do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_salvar
def test_ct068_hamburguinho_padrao_salvar(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Localiza o switch sessão visível e clica
    page.locator("div.ant-collapse-content-box >> button[role='switch']").nth(3).click(force=True)
    # Clicar no botão pelo texto Save Alterações
    page.locator("button:has-text('Save Alterações')").click()
    aviso = page.locator("text=Alterações salvas com sucesso!")
    expect(aviso).to_be_visible()
    # Localiza o título
    title = page.locator("h1._title_1y42z_14").nth(0)
    expect(title).to_contain_text("Fluxo de Caixa")
    print("Alterações salvas com sucesso!")


#Objetivo do teste: Validar o funcionamento da opção "cancelar" do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_cancelar
def test_ct069_hamburguinho_padrao_cancelar(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no botão pelo texto Cancel
    page.locator("button:has-text('Cancel')").click()
    preset_element = page.locator("strong:has-text('Preset: Padrão')")
    expect(preset_element).not_to_be_visible()
    print("Clicado em cancelar com sucesso")


#Objetivo do teste: Validar o funcionamento da opção "fechar" do hamburguinho padrão
@pytest.mark.hamburguinho_padrao_fechar
def test_ct070_hamburguinho_padrao_fechar(page):
    #Clica no botão "Padrão"
    page.locator("#preset-dropdown-button").click()
    # Clica no botão usando o texto
    page.locator("button:has-text('Editar')").nth(0).click()
    # Clicar no botão de fechar
    page.locator("button[aria-label='Close']").click()
    preset_element = page.locator("strong:has-text('Preset: Padrão')")
    expect(preset_element).not_to_be_visible()
    print("Clicado em fechar com sucesso")


#Objetivo do teste: Validar o funcionamento do menu hamburguinho e a visibilidade do texto "Configurar Resumos financeiros"
@pytest.mark.hamburguinho_resumos_financeiros
def test_ct071_hamburguinho_resumos_financeiros(page):
    #Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Verifica se o texto "Configurar Resumos financeiros" está visível
    expect(page.get_by_text("Configurar Resumos financeiros")).to_be_visible()
    print("✅ Texto 'Configurar Resumos financeiros' está visível na tela.")


#Objetivo do teste: Validar o funcionamento dos check e uncheck dos switches do hamburguinho do "Resumos Financeiros"
@pytest.mark.hamburguinho_resumos_financeiros_check

def test_ct072_resumos_financeiros_hamburguinho_check_uncheck(page):
    # Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    switch_ids = [
        "resumos-financeiros-indice-receitas-switch",
        "resumos-financeiros-indice-despesas-switch",
        "resumos-financeiros-atrasos-receber-switch",
        "resumos-financeiros-saldo-switch",
        "resumos-financeiros-expand-receitas-switch",
        "resumos-financeiros-expand-despesas-switch",
        "resumos-financeiros-expand-atrasos-switch",
        "resumos-financeiros-expand-saldo-switch",
    ]
    for switch_id in switch_ids:
        sw = page.locator(f"#{switch_id}")
        # Pega o estado inicial
        initial_state = sw.get_attribute("aria-checked")
        print(f"🔹 Estado inicial do switch '{switch_id}': {initial_state}")
        # Calcula o estado invertido
        target_state = "false" if initial_state == "true" else "true"
        # Clica para alternar
        sw.click()
        time.sleep(1)
        # Espera até que o atributo tenha o novo valor
        expect(sw).to_have_attribute("aria-checked", target_state)
        print(f"✅ Switch '{switch_id}' mudou de {initial_state} para {target_state}")
        # Clica novamente para retornar ao estado original
        sw.click()
        expect(sw).to_have_attribute("aria-checked", initial_state)
        print(f"✅ Switch '{switch_id}' voltou ao estado inicial ({initial_state})")


#Objetivo do teste: Validar o funcionamento do check e uncheck do switch "Sessão Visisel" do Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_session_visible_switch

def test_ct073_resumos_financeiros_hamburguinho_sessao_visivel(page):
    # Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    sessao_switch = page.locator("#resumos-financeiros-sessao-switch")
    # Pega estado inicial
    initial_state = sessao_switch.get_attribute("aria-checked")
    print(f"🔹 Estado inicial: {initial_state}")
    # 1️⃣ Se estiver marcado, clicar para desmarcar
    if initial_state == "true":
        sessao_switch.click()
        expect(sessao_switch).to_have_attribute("aria-checked", "false")
        print("✅ Sessão Visível desmarcada.")
    else:
        print("ℹ️ Sessão Visível já desmarcada.")
    # 2️⃣ Clicar para marcar
    sessao_switch.click()
    expect(sessao_switch).to_have_attribute("aria-checked", "true")
    print("✅ Sessão Visível marcada novamente.")
    

#Objetivo do teste: Validar o funcionamento do botão fechar (X) no menu hamburguinho Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_fechar
def test_ct074_resumos_financeiros_hamburguinho_fechar(page):
    #Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Configure Card Preset")).not_to_be_visible()
    print("✅ Menu fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão salvar no menu hamburguinho Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_salvar
def test_ct075_resumos_financeiros_hamburguinho_salvar(page):
    #Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Verifica se o menu foi fechado
    aviso = page.locator("text=Preset de resumos financeiros salvo com sucesso!")
    expect(page.get_by_text("Configure Card Preset")).not_to_be_visible()
    expect(aviso).to_be_visible()
    print("✅ Menu salvo e fechado corretamente.")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ocultar_indice_receitas
def test_ct076_resumos_financeiros_hamburguinho_ocultar_indice_receitas(page):
    # Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Localiza o switch
    switch = page.locator("#resumos-financeiros-indice-receitas-switch")
    if switch.get_attribute("aria-checked") == "true":
        switch.click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    time.sleep(2)
    # Verifica que o título não está visível
    title = page.get_by_role("heading", name="Índice Receitas")
    expect(title).not_to_be_visible()
    print("✅ Switch 'Índice Receitas' ocultado corretamente.")



#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice despesas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ocultar_indice_despesas
def test_ct077_resumos_financeiros_hamburguinho_ocultar_indice_despesas(page):
    page.locator("#resumos-financeiros-menu-button").click()
    switch = page.locator("#resumos-financeiros-indice-despesas-switch")
    if switch.get_attribute("aria-checked") == "true":
        switch.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    title = page.get_by_role("heading", name="Índice Despesas")
    expect(title).not_to_be_visible()
    print("✅ Switch 'Índice Despesas' ocultado corretamente.")



#Objetivo do teste: Validar o funcionamento de ocultar o switch "Atrasos a receber" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ocultar_atrasos_a_receber
def test_ct078_resumos_financeiros_hamburguinho_ocultar_atrasos_a_receber(page):
    page.locator("#resumos-financeiros-menu-button").click()
    switch = page.locator("#resumos-financeiros-atrasos-receber-switch")
    if switch.get_attribute("aria-checked") == "true":
        switch.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    title = page.get_by_role("heading", name="Atrasos a Receber")
    expect(title).not_to_be_visible()
    print("✅ Switch 'Atrasos a Receber' ocultado corretamente.")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Saldo de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ocultar_saldo
def test_ct079_resumos_financeiros_hamburguinho_ocultar_saldo(page):
    page.locator("#resumos-financeiros-menu-button").click()
    switch = page.locator("#resumos-financeiros-saldo-switch")
    if switch.get_attribute("aria-checked") == "true":
        switch.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    title = page.get_by_role("heading", name="Saldo")
    expect(title).not_to_be_visible()
    print("✅ Switch 'Saldo' ocultado corretamente.")



#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_desabilitar_indice_receitas_iniciar_cards
def test_ct080_hamburguinho_resumos_financeiros_desabilitar_indice_receitas_iniciar_cards(page):
    # Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Localiza todos os switches na página
    indice_receitas = page.locator("#resumos-financeiros-indice-receitas-switch")
    # Só clica se estiver marcado (true)
    if indice_receitas.get_attribute("aria-checked") == "true":
        indice_receitas.click()
        print("✅ 'Índice Receitas' foi desmarcado.")
    else:
        print("ℹ️ 'Índice Receitas' já estava desmarcado.")
    # Seleciona o respectivo switch da sessão 'Iniciar cards'
    iniciar_cards = page.locator("#resumos-financeiros-expand-receitas-switch")
    # Verifica se está desabilitado
    expect(iniciar_cards).not_to_be_enabled()
    print("✅ Switch 'Índice Receitas' na sessão 'Iniciar cards com tabela expandida' não pode ser habilitado")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice despesas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_desabilitar_indice_despesas_iniciar_cards
def test_ct081_hamburguinho_resumos_financeiros_desabilitar_indice_despesas_iniciar_cards(page):
    page.locator("#resumos-financeiros-menu-button").click()
    indice_despesas = page.locator("#resumos-financeiros-indice-despesas-switch")
    if indice_despesas.get_attribute("aria-checked") == "true":
        indice_despesas.click()
        print("✅ 'Índice Despesas' foi desmarcado.")
    else:
        print("ℹ️ 'Índice Despesas' já estava desmarcado.")
    iniciar_cards = page.locator("#resumos-financeiros-expand-despesas-switch")
    expect(iniciar_cards).not_to_be_enabled()
    print("✅ Switch 'Índice Despesas' na sessão 'Iniciar cards com tabela expandida' não pode ser habilitado")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Atrasos a receber" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_desabilitar_atrasos_a_receber_iniciar_cards
def test_ct082_hamburguinho_resumos_financeiros_desabilitar_atrasos_a_receber_iniciar_cards(page):
    page.locator("#resumos-financeiros-menu-button").click()
    atrasos_a_receber = page.locator("#resumos-financeiros-atrasos-receber-switch")
    if atrasos_a_receber.get_attribute("aria-checked") == "true":
        atrasos_a_receber.click()
        print("✅ 'Atrasos a Receber' foi desmarcado.")
    else:
        print("ℹ️ 'Atrasos a Receber' já estava desmarcado.")
    iniciar_cards = page.locator("#resumos-financeiros-expand-atrasos-switch")
    expect(iniciar_cards).not_to_be_enabled()
    print("✅ Switch 'Atrasos a Receber' na sessão 'Iniciar cards com tabela expandida' não pode ser habilitado")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Saldo" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_desabilitar_saldo_iniciar_cards
def test_ct083_hamburguinho_resumos_financeiros_desabilitar_saldo_iniciar_cards(page):
    page.locator("#resumos-financeiros-menu-button").click()
    saldo = page.locator("#resumos-financeiros-saldo-switch")
    if saldo.get_attribute("aria-checked") == "true":
        saldo.click()
        print("✅ 'Saldo' foi desmarcado.")
    else:
        print("ℹ️ 'Saldo' já estava desmarcado.")
    iniciar_cards = page.locator("#resumos-financeiros-expand-saldo-switch")
    expect(iniciar_cards).not_to_be_enabled()
    print("✅ Switch 'Saldo' na sessão 'Iniciar cards com tabela expandida' não pode ser habilitado")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_iniciar_cards_indice_receitas
def test_ct084_hamburguinho_resumos_financeiros_iniciar_cards_indice_receitas(page):
    # Clica no menu hamburguinho do Resumos Financeiros
    page.locator("#resumos-financeiros-menu-button").click()
    # Localiza todos os switches na página
    indice_receitas = page.locator("#resumos-financeiros-indice-receitas-switch")
    # Só clica se estiver desmarcado (false)
    if indice_receitas.get_attribute("aria-checked") == "false":
        indice_receitas.click()
        print("✅ 'Índice Receitas' foi marcado.")
    else:
        print("ℹ️ 'Índice Receitas' já estava marcado.")
    # Seleciona o respectivo switch da sessão 'Iniciar cards'
    expand_receitas = page.locator("#resumos-financeiros-expand-receitas-switch")
    if expand_receitas.get_attribute("aria-checked") == "false":
        expand_receitas.click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    botao_ver_esconder_tabela = page.locator("#indice-receitas-ver-tabela-button")
    expect(botao_ver_esconder_tabela).to_have_text("Esconder Tabela")
    time.sleep(2)
    print("✅ Botão 'Esconder Tabela' e a Tabela de 'Índices Receitas' estão visíveis")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Índice Despesas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_iniciar_cards_indice_despesas
def test_ct085_hamburguinho_resumos_financeiros_iniciar_cards_indice_despesas(page):
    page.locator("#resumos-financeiros-menu-button").click()
    indice_despesas = page.locator("#resumos-financeiros-indice-despesas-switch")
    if indice_despesas.get_attribute("aria-checked") == "false":
        indice_despesas.click()
        print("✅ 'Índice Despesas' foi marcado.")
    else:
        print("ℹ️ 'Índice Despesas' já estava marcado.")
    expand_despesas = page.locator("#resumos-financeiros-expand-despesas-switch")
    if expand_despesas.get_attribute("aria-checked") == "false":
        expand_despesas.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    botao_tabela = page.locator("#indice-despesas-ver-tabela-button")
    expect(botao_tabela).to_have_text("Esconder Tabela")
    print("✅ Botão 'Esconder Tabela' e a Tabela de 'Índices Despesas' estão visíveis")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Atrasos a Receber" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_iniciar_cards_atrasos_a_receber
def test_ct086_hamburguinho_resumos_financeiros_iniciar_cards_atrasos_a_receber(page):
    page.locator("#resumos-financeiros-menu-button").click()
    atrasos_a_receber = page.locator("#resumos-financeiros-atrasos-receber-switch")
    if atrasos_a_receber.get_attribute("aria-checked") == "false":
        atrasos_a_receber.click()
        print("✅ 'Atrasos a Receber' foi marcado.")
    else:
        print("ℹ️ 'Atrasos a Receber' já estava marcado.")
    expand_atrasos = page.locator("#resumos-financeiros-expand-atrasos-switch")
    if expand_atrasos.get_attribute("aria-checked") == "false":
        expand_atrasos.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    botao_tabela = page.locator("#atrasos-a-receber-ver-tabela-button")
    expect(botao_tabela).to_have_text("Esconder Tabela")
    print("✅ Botão 'Esconder Tabela' e a Tabela de 'Atrasos a Receber' estão visíveis")


#Objetivo do teste: Validar o funcionamento de ocultar o switch "Saldo" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_iniciar_cards_saldo
def test_ct087_hamburguinho_resumos_financeiros_iniciar_cards_saldo(page):
    page.locator("#resumos-financeiros-menu-button").click()
    saldo = page.locator("#resumos-financeiros-saldo-switch")
    if saldo.get_attribute("aria-checked") == "false":
        saldo.click()
        print("✅ 'Saldo' foi marcado.")
    else:
        print("ℹ️ 'Saldo' já estava marcado.")
    expand_saldo = page.locator("#resumos-financeiros-expand-saldo-switch")
    if expand_saldo.get_attribute("aria-checked") == "false":
        expand_saldo.click()
    page.click("button:has-text('Save')")
    time.sleep(2)
    botao_tabela = page.locator("#saldo-ver-tabela-button")
    expect(botao_tabela).to_have_text("Esconder Tabela")
    print("✅ Botão 'Esconder Tabela' e a Tabela de 'Saldo' estão visíveis")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_visivel
def test_ct088_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_visivel(page):
    botao = page.locator("#indice-receitas-ver-tabela-button")
    # Verifica o texto do botão
    if botao.inner_text() == "Ver Tabela":
        botao.click()
        print("✅ Botão 'Ver Tabela' clicado para exibir a tabela.")
    else:
        print("ℹ️ Botão já estava em 'Esconder Tabela'. Nenhuma ação necessária.")
    # No final garante que a tabela está visível
    container_botoes = page.locator("div._card_table_ydohh_46")
    expect(container_botoes).to_be_visible()
    print("✅ Container de 'Índice Receitas' está visível.")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_config
def test_ct089_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_config(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão pelo title
    page.locator("button[title='Configurar tabela']").click()
    print("✅ Botão 'Configurar tabela' clicado")
    # Localiza o título do drawer
    titulo = page.locator("div.ant-drawer-title", has_text="Configurar tabela")
    expect(titulo).to_be_visible()
    print("✅ Drawer 'Configurar tabela' está visível")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações -> filtro de agrupamento padrão" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_projeto
def test_ct090_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_projeto(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no Select
    page.locator(".ant-select-selector").click()
    page.locator(".ant-select-item-option-content", has_text="Projeto").click()  # Seleciona "Projeto"
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # verifica se mostra o aviso
    aviso = page.locator("text=Configuração da tabela salva com sucesso!")
    expect(aviso).to_be_visible()
    #verifica se o modal das configurações não aparece mais
    titulo = page.locator("div.ant-drawer-title", has_text="Configurar tabela")
    expect(titulo).not_to_be_visible()
    #Verifica se no dropdown mostra "Projeto"
    dropdown = page.locator("select._grouping_dropdown_19ify_46")
    dropdown.select_option("projeto_nome")
    expect(dropdown).to_have_value("projeto_nome") 
    print("Acessado 'Projeto' em Índice Receitas")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações -> filtro de agrupamento padrão" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_centro_custo
def test_ct091_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_centro_custo(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no Select
    page.locator(".ant-select-selector").click()
    page.locator(".ant-select-item-option-content", has_text="Centro de Custo").click()  # Seleciona "Centro de Custo"
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # verifica se mostra o aviso
    aviso = page.locator("text=Configuração da tabela salva com sucesso!")
    expect(aviso).to_be_visible()
    #verifica se o modal das configurações não aparece mais
    titulo = page.locator("div.ant-drawer-title", has_text="Configurar tabela")
    expect(titulo).not_to_be_visible()
    #Verifica se no dropdown mostra "Centro de Custo"
    dropdown = page.locator("select._grouping_dropdown_19ify_46")
    dropdown.select_option("centro_de_custo_nome")
    expect(dropdown).to_have_value("centro_de_custo_nome") 
    print("Acessado 'Centro de Custo' em Índice Receitas")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações -> filtro de agrupamento padrão" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_plano_financeiro
def test_ct092_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_plano_financeiro(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no Select
    page.locator(".ant-select-selector").click()
    page.locator(".ant-select-item-option-content", has_text="Plano Financeiro").click()  # Seleciona "Plano Financeiro"
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # verifica se mostra o aviso
    aviso = page.locator("text=Configuração da tabela salva com sucesso!")
    expect(aviso).not_to_be_visible()
    #verifica se o modal das configurações não aparece mais
    titulo = page.locator("div.ant-drawer-title", has_text="Configurar tabela")
    expect(titulo).to_be_visible()
    #Verifica se no dropdown mostra "Plano Financeiro"
    dropdown = page.locator("select._grouping_dropdown_19ify_46")
    dropdown.select_option("plano_financeiro_nome")
    expect(dropdown).to_have_value("plano_financeiro_nome") 
    print("Acessado 'Plano Financeiro' em Índice Receitas")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações -> filtro de agrupamento padrão" em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_empresa
def test_ct093_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_filtro_agrup_empresa(page):
    # Localiza e clica no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no Select
    page.locator(".ant-select-selector").click()
    # Aguarda o dropdown aparecer e clica em "Empresa"
    option = page.locator(".ant-select-item-option-content", has_text="Empresa").first
    option.wait_for(state="visible")
    option.click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Verifica se mostra o aviso
    aviso = page.locator("text=Configuração da tabela salva com sucesso!")
    expect(aviso).not_to_be_visible()
    # Verifica se o modal das configurações não aparece mais
    titulo = page.locator("div.ant-drawer-title", has_text="Configurar tabela")
    expect(titulo).to_be_visible()
    # Verifica se no dropdown mostra "Empresa"
    dropdown = page.locator("select._grouping_dropdown_19ify_46")
    dropdown.select_option("empresa_nome")
    expect(dropdown).to_have_value("empresa_nome") 
    print("✅ Acessado 'Empresa' em Índice Receitas")


#Objetivo do teste: Validar o funcionamento do botão "Ver Tabela -> Configurações -> colunas visíveis"  em "Índice Receitas" de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_colunas_visiveis
def test_ct094_hamburguinho_resumos_financeiros_ver_tabela_indice_receitas_colunas_visiveis(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
 # Seleciona todos os checkboxes 
    checkboxes = page.locator("input.ant-checkbox-input[type='checkbox']")
    
    count = checkboxes.count()
    for i in range(count):
        # Pega o checkbox pelo índice
        cb = checkboxes.nth(i)
        # Clica 2x de forma separada
        cb.click()
        expect(cb).not_to_be_checked()
        print(f"Check {i} desmarcado")
        cb.click()
        expect(cb).to_be_checked()
        print(f"Check {i} marcado novamente")


#Objetivo do teste: Validar o funcionamento de ocultar o ckeckbox "Nome" da tabela Índice Receitas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_nome
def test_ct095_hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_nome(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Localiza o checkbox
    checkbox = page.locator("input.ant-checkbox-input[type='checkbox'][value='nome']")
    # Verifica se está marcado
    if checkbox.is_checked():
        checkbox.click()  # desmarca somente se estiver marcado
    time.sleep(1)   
    # Clicar em salvar
    page.locator("button:has-text('Save')").click()
    # Localiza a div do header que contém o texto "Nome"
    nome_header = page.locator("//div[contains(@class,'ag-cell-label-container') and .//span[text()='Nome']]")
    # Verifica que NÃO está visível
    expect(nome_header).not_to_be_visible()
    print("Ckeckbox 'Nome' desabilitado e não mostrado na tabela")


#Objetivo do teste: Validar o funcionamento de ocultar o ckeckbox "Id" da tabela Índice Receitas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_id
def test_ct096_hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_id(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Localiza o checkbox
    checkbox = page.locator("input.ant-checkbox-input[type='checkbox'][value='id']")
    # Verifica se está marcado
    if checkbox.is_checked():
        checkbox.click()  # desmarca somente se estiver marcado
    time.sleep(1)   
    # Clicar em salvar
    page.locator("button:has-text('Save')").click()
    # Localiza a div pelo conjunto de classes (todas juntas para ser específico)
    header_div = page.locator("div.ag-cell-label-container.ag-header-cell-sorted-desc[role='presentation']")
    # Verifica que NÃO está visível
    expect(header_div).not_to_be_visible()
    print("Ckeckbox 'ID' desabilitado e não mostrado na tabela")


#Objetivo do teste: Validar o funcionamento de ocultar o ckeckbox "Incorrido" da tabela Índice Receitas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_incorrido
def test_ct097_hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_incorrido(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Localiza o checkbox
    checkbox = page.locator("input.ant-checkbox-input[type='checkbox'][value='incorrido']")
    # Verifica se está marcado
    if checkbox.is_checked():
        checkbox.click()  # desmarca somente se estiver marcado
    time.sleep(1)   
    # Clicar em salvar
    page.locator("button:has-text('Save')").click()
    # Localiza a div do header que contém o texto "Incorrido"
    incorrido_header = page.locator(
        "//div[contains(@class,'ag-header-cell') and .//span[text()='Incorrido']]"    )
    # Verifica que NÃO está visível
    expect(incorrido_header).not_to_be_visible()
    print("Ckeckbox 'Incorrido' desabilitado e não mostrado na tabela")


#Objetivo do teste: Validar o funcionamento de ocultar o ckeckbox "A incorrer" da tabela Índice Receitas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_a_incorrer
def test_ct098_hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_a_incorrer(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Localiza o checkbox
    checkbox = page.locator("input.ant-checkbox-input[type='checkbox'][value='a_incorrer']")
    # Verifica se está marcado
    if checkbox.is_checked():
        checkbox.click()  # desmarca somente se estiver marcado
    time.sleep(1)   
    # Clicar em salvar
    page.locator("button:has-text('Save')").click()
    # Localiza a div do header que contém o texto "A Incorrer"
    a_incorrer_header = page.locator("//div[contains(@class,'ag-header-cell') and .//span[text()='A Incorrer']]").first
    # Verifica que NÃO está visível
    expect(a_incorrer_header).not_to_be_visible()
    print("Ckeckbox 'A incorrer' desabilitado e não mostrado na tabela")


#Objetivo do teste: Validar o funcionamento de ocultar o ckeckbox "Nome" da tabela Índice Receitas de Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_comprometido
def test_ct099_hamburguinho_resumos_financeiros_tabela_indices_receitas_config_colunas_visiveis_ocultar_comprometido(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Localiza o checkbox
    checkbox = page.locator("input.ant-checkbox-input[type='checkbox'][value='comprometido']")
    # Verifica se está marcado
    if checkbox.is_checked():
        checkbox.click()  # desmarca somente se estiver marcado
    time.sleep(1)   
    # Clicar em salvar
    page.locator("button:has-text('Save')").click()
    # Localiza o header da coluna 'Committed' usando o col-id
    comprometido_header = page.locator("div.ag-header-cell[col-id='comprometido']")
    # Pega o container interno do label
    comprometido_label_container = comprometido_header.locator("div.ag-cell-label-container").nth(1)
    # Verifica que NÃO está visível
    expect(comprometido_label_container).not_to_be_visible()
    print("Ckeckbox 'comprometido' desabilitado e não mostrado na tabela")


#Objetivo do teste: Validar o funcionamento do botão fechar (X) no menu hamburguinho Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indice_receitas_config_fechar
def test_ct100_hamburguinho_resumos_financeiros_tabela_indice_receitas_config_fechar(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no ícone de fechar (X) no canto superior direito
    page.click("button[aria-label='Close']")
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Configurar tabela")).not_to_be_visible()
    print("✅ Menu fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão salvar no menu hamburguinho Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indice_receitas_config_salvar
def test_ct101_hamburguinho_resumos_financeiros_tabela_indice_receitas_config_salvar(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clica no botão Save
    page.click("button:has-text('Save')")
    # Verifica se o menu foi fechado
    aviso = page.locator("text=Configuração da tabela salva com sucesso!")
    expect(page.get_by_text("Configurar tabela")).not_to_be_visible()
    expect(aviso).to_be_visible()
    print("✅ Menu salvo e fechado corretamente.")


#Objetivo do teste: Validar o funcionamento do botão cancelar (X) no menu hamburguinho Resumos Financeiros
@pytest.mark.hamburguinho_resumos_financeiros_tabela_indice_receitas_config_cancelar
def test_ct102_hamburguinho_resumos_financeiros_tabela_indice_receitas_config_cancelar(page):
    # Localiza e clina no botão pelo texto "Ver Tabela"
    page.locator("#indice-receitas-ver-tabela-button").click()
    # Localiza o contêiner
    container_botoes = page.locator("div._buttons_container_19ify_40")
    # Localiza e clica no botão Configurações
    page.locator("button[title='Configurar tabela']").click()
    # Clicar pelo texto do botão
    page.locator("button:has-text('Cancel')").click()
    # Verifica se o menu foi fechado
    expect(page.get_by_text("Configurar tabela")).not_to_be_visible()
    print("✅ Menu fechado corretamente.")
