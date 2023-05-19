describe('TVTropes 2.0 PoC', () => {
  it('creates a trope page', () => {
    cy.visit('http://localhost:8000/nuke')
    cy.visit('http://localhost:8000/switchUser?user=karen');
    cy.visit('http://localhost:8000/createPage')
    cy.get('input#path').should('have.length', 1)
    cy.get('input#displayName').should('have.length', 1)
    cy.get('input#path').type('Main/TestTrope')
    cy.get('input#displayName').type('Test trope')
    cy.get('#pageType_1').click()
    cy.get('form').submit()
    cy.get('h1').should('have.text', 'Test trope')
  })

  it('creates a work page', () => {
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/createPage')
    cy.get('input#path').type('Literature/TestWork')
    cy.get('input#displayName').type('Test work')
    cy.get('#pageType_0').click()
    cy.get('form').submit()
    cy.get('h1').should('have.text', 'Literature / Test work')
  })

  var createEx=function(num, asym){
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#nxp > input').click()
    cy.get('#srcNew').type("t")
    cy.get('.suggestion').should('have.length', 1)
    cy.get('.suggestion').should('have.text', 'Test trope (Main/TestTrope)')
    cy.get('.suggestion').click()
    cy.get('#exeditNew').type("Example text "+num)
    cy.get('#playWithTypeNew').select(""+(num))
    if (asym) cy.get('#asymNew').click()
    cy.get('#exgetprvNew').click()
    cy.get('#expreviewNew').should('have.text', 'Test trope: '+(num==1?'Averted: ':'')+'Example text '+num)
    cy.get('input[value="back to edit"]').click()
    cy.get('#exeditNew').should('have.value', 'Example text '+num)
    cy.get('#exgetprvNew').click()
    cy.get('input[value="save"]').click()
    cy.get('#example'+num).should('have.length', 1)
    cy.get('#example'+num).should('have.text', 'Test trope: '+(num==1?'Averted: ':'')+'Example text '+num)
  }

  it('creates a symmetric example', () => {
      createEx(0, false);
  })

  it('creates an asymmetric example', () => {
      createEx(1, true);
  })

  it('edits examples on work page', () => {
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#example0 > input').should('have.length', 1)
    cy.get('#example0 > input').click()
    cy.get('#asym0').should('have.length', 1)
    cy.get('#asym0').should('not.be.checked')
    cy.get('#playWithType0').should('have.value', 0)
    cy.get('#exedit0').type(" on work page")
    cy.get('#exgetprv0').click()
    cy.get('#example0 > > input[value="save"]').click()

    cy.get('#example1 > input').click()
    cy.get('#asym1').should('have.length', 1)
    cy.get('#asym1').should('be.checked')
    cy.get('#playWithType1').should('have.value', 1)
    cy.get('#exedit1').type(" on work page")
    cy.get('#exgetprv1').click()
    cy.get('#example1 > > input[value="save"]').click()

    cy.get('#block1 > input').click()
    cy.get('#bledit1').type("block description")
    cy.get('#blgetprv1').click()
    cy.get('#block1 > > input[value="save"]').click()
  })

  it('edits asym element', () => {
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/Main/TestTrope')
    cy.get('#addHidden').should('have.length', 1)
    cy.get('#example0').should('have.text', 'Example text 0 on work page')
    cy.get('#example1').should('have.text', 'Averted: Example text 1')

    cy.get('input[onclick="edit()"]').click()
    cy.get('#example1 > input').click()
    cy.get('#exedit1').type(" on trope page")
    cy.get('#playWithType1').select(3)
    cy.get('#exgetprv1').click()
    cy.get('#example1 > > input[value="save"]').click()

    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('#example1').should('have.text', 'Inverted: Example text 1 on work page')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#example1 > input').click()
    cy.get('#playWithType1').should('have.value', 3)
    cy.get('#exedit1').should('have.value', 'Example text 1 on work page')

  })

  it('hides an example', () => {
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#example0 > input').click()
    cy.get('#hide0').should('have.length', 1)
    cy.get('#hide0').should('not.be.checked')
    cy.get('#hide0').click()
    cy.get('#exgetprv0').click()
    cy.get('#example0 > > input[value="save"]').click()
    cy.get('#example0 > span[class="hidden"]').should('have.length', 1)
  
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('#example0').should('have.length', 0)
    cy.get('#addHidden').click()
    cy.get('#example0').should('have.length', 1)
    cy.get('#example0 > span[class="hidden"]').should('have.length', 1)

    cy.get('input[onclick="edit()"]').click()
    cy.get('#example0 > input').click() // the "hidden" formatter should not prevent clicking the button
    cy.get('#hide0').click()
    cy.get('#exgetprv0').click()
    cy.get('#example0 > > input[value="save"]').click()

    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('#example0').should('have.length', 1)
  })

  it('locks an example', () => {
    cy.visit('http://localhost:8000/switchUser?user=karen');
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#example0 > input').click()
    cy.get('#lock0').should('have.length', 1)
    cy.get('#lock0').should('not.be.checked')
    cy.get('#lock0').click()
    cy.get('#exgetprv0').click()
    cy.get('#example0 > > input[value="save"]').click()
  
    cy.visit('http://localhost:8000/switchUser?user=alice');
    cy.visit('http://localhost:8000/Literature/TestWork')
    cy.get('input[onclick="edit()"]').click()
    cy.get('#example0 > input').click()
    cy.get('#exgetprv0').should('have.length', 0)
    cy.get('#src0').should('be.disabled')
    cy.get('#tgt0').should('be.disabled')
    cy.get('#playWithType0').should('be.disabled')
    cy.get('#asym0').should('be.disabled')
    cy.get('#hide0').should('be.disabled')
    cy.get('#exedit0').should('be.disabled')
  })

  afterEach(function() {
    if (this.currentTest.state === 'failed') {
      Cypress.runner.end();
    }
  })

})
