import React, { Component } from 'react';
import $ from 'jquery';
import '../stylesheets/FormView.css';

class FormView extends Component {
  constructor(props) {
    super(props);
    this.state = {
      question: '',
      answer: '',
      difficulty: 1,
      category: 1,
      categories: {},
    };
  }

  componentDidMount() {
    $.ajax({
      url: `/categories`, //TODO: update request URL
      type: 'GET',
      success: (result) => {
        if (result && result.categories) {
          this.setState({ categories: result.categories });
          console.log('Fetched categories:', result.categories);
          return;
        } else {
          this.setState({ categories: {} });
          return;
        }
      },
      error: (error) => {
        console.error('Category fetch error:', error); 
        alert('Unable to load categories. Please try your request again');
        return;
      },
    });
  }

  submitQuestion = (event) => {
    event.preventDefault();
    $.ajax({
      url: '/questions', //TODO: update request URL
      type: 'POST',
      dataType: 'json',
      contentType: 'application/json',
      data: JSON.stringify({
        question: this.state.question,
        answer: this.state.answer,
        difficulty: this.state.difficulty,
        category: this.state.category,
      }),
      xhrFields: {
        withCredentials: true,
      },
      crossDomain: true,
      success: (result) => {
        document.getElementById('add-question-form').reset();
        return;
      },
      error: (error) => {
        alert('Unable to add question. Please try your request again');
        return;
      },
    });
  };

  handleChange = (event) => {
    this.setState({ [event.target.name]: event.target.value });
  };

  render() {
    const { categories } = this.state;
    
    return (
      <div id='add-form'>
        <h2>Add a New Trivia Question</h2>
        <form
          className='form-view'
          id='add-question-form'
          onSubmit={this.submitQuestion}
        >
          <label>
            Question
            <input type='text' name='question' value={this.state.question} onChange={this.handleChange} />
          </label>
          <label>
            Answer
            <input type='text' name='answer' value={this.state.answer} onChange={this.handleChange} />
          </label>
          <label>
            Difficulty
            <select name='difficulty' value={this.state.difficulty} onChange={this.handleChange}>
              <option value='1'>1</option>
              <option value='2'>2</option>
              <option value='3'>3</option>
              <option value='4'>4</option>
              <option value='5'>5</option>
            </select>
          </label>
          <label>
            Category
            <select name='category' value={this.state.category} onChange={this.handleChange} >
              {Object.keys(categories).length > 0 ? (
                Object.keys(categories).map((id) => (
                  <option key={id} value={id}>
                    {categories[id]}
                  </option>
                ))
              ) : (
                <option value='' disabled>
                 No categories available 
                </option>
              )}
            </select>
          </label>
          <input type='submit' className='button' value='Submit' />
        </form>
      </div>
    );
  }
}

export default FormView;
