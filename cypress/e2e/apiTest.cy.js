describe('API Create user test', () => {
  it('create user', () => {
    cy.request('POST', 'http://127.0.0.1:8000/users/', {
      name: 'test2',
      age: 15,
    }).then((response) => {
      expect(response.status).to.equal(200);
      expect(response.body).to.have.property('name', 'test2');
      expect(response.body).to.have.property('age', 15);
      expect(response.body).to.have.property('id'); // Проверка наличия `id`
    });
  });
  it('create post test', () => {
    cy.request('POST', 'http://127.0.0.1:8000/posts/', {
        title: "post1",
        body: "some body1",
        author_id: 1,
    }).then((response) => {
        expect(response.status).to.equal(200);
        expect(response.body).to.have.property('title', 'post1');
        expect(response.body).to.have.property('body', 'some body1');
        expect(response.body).to.have.property('author_id', 1); 
        expect(response.body).to.have.property('id');

        expect(response.body).to.have.property('author');
        expect(response.body.author).to.have.property('name');
        expect(response.body.author).to.have.property('age');
        expect(response.body.author).to.have.property('id');
    })
  })
});
