
# Testes de Interface — Selenium

Este repositório contém scripts de automação de testes de interface (UI) usando **Selenium WebDriver**, escritos para demonstrar diferentes formas de localizar elementos com *locators*.  
**Atenção:** os locators usados nos testes são exemplos e podem não refletir exatamente os elementos reais da aplicação alvo.

---

## 🎯 Objetivo

- Praticar automação de UI com Selenium  
- Demonstrar uso de diferentes estratégias de localização (ID, CSS Selector, XPath, etc)  
- Criar testes simples que simulam interações típicas de usuários  

---

## 🔧 Tecnologias

- Selenium WebDriver  
- Linguagem: **JavaScript / Python / Java / outra** *(adapte de acordo com seu código)*  
- Navegadores suportados: Chrome, Firefox, outros compatíveis com Selenium  
- Ferramentas de teste: estrutura de testes (ex: Mocha, Jest, Pytest) *(se você estiver usando)*  

---

## 📂 Estrutura do Projeto

```

/tests
├── exemplo-login.spec.js      # Teste de login
├── exemplo-formulario.spec.js # Teste de formulário
/support
└── selenium-helpers.js        # Funções úteis para reutilização

````

*(A estrutura pode variar dependendo de como você organizou o repositório.)*

---

## 🚀 Como executar os testes

1. Certifique-se de ter o **Node.js / Python** instalado (dependendo do projeto).  
2. Instale as dependências:  
   ```bash
   npm install        # para projetos JS  
   # ou  
   pip install -r requirements.txt  # para Python  
````

3. Baixe os drivers do navegador (ex: ChromeDriver) compatíveis com a versão do seu navegador.
4. Execute os testes:

   ```bash
   npx mocha tests       # para JS + Mocha  
   # ou  
   pytest tests/         # para Python  
   ```

---

## 💡 Sobre os Locators

* Os locators usados nos scripts são **exemplos**: eles podem não corresponder exatamente à aplicação real.
* Use esses exemplos como ponto de partida para definir seus próprios locators mais robustos.
* Recomenda-se usar boas práticas de localização para evitar fragilidade nos testes.

---

## ✅ Próximos Passos

* Substituir os locators por versões reais para a aplicação que está testando
* Adicionar mais cenários de teste: navegação, logout, validações, erros de formulário
* Integrar os testes a um pipeline CI/CD
* Implementar Page Object Model (POM) para organizar melhor os testes

---

## 📚 Referências úteis

* [Documentação Selenium WebDriver](https://www.selenium.dev/pt-br/documentation/overview/) ([Selenium][1])
* [Primeiro script Selenium (Getting started)](https://www.selenium.dev/pt-br/documentation/webdriver/getting_started/first_script/) ([Selenium][2])

---

## 🎓 Autora

Daniela Foggiatto — QA Automação
[Perfil no GitHub](https://github.com/danielafoggiatto)

---

